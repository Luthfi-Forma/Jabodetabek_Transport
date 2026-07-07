// Mesin simulasi: jadwal + geometri jalur -> posisi kendaraan pada waktu t.
//
// Prinsip (sama dengan mini-tokyo-3d): posisi kereta dihitung murni dari
// timetable. Antar stasiun dipakai easing kubik supaya kereta terlihat
// mengerem masuk stasiun dan berakselerasi keluar.

const R_EARTH_KM = 6371.0088;

function haversineKm(a, b) {
  const dLat = ((b[1] - a[1]) * Math.PI) / 180;
  const dLon = ((b[0] - a[0]) * Math.PI) / 180;
  const la1 = (a[1] * Math.PI) / 180;
  const la2 = (b[1] * Math.PI) / 180;
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(la1) * Math.cos(la2) * Math.sin(dLon / 2) ** 2;
  return 2 * R_EARTH_KM * Math.asin(Math.sqrt(h));
}

function easeInOutCubic(x) {
  return x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2;
}

export function createEngine(linesJson, linesGeojson, timetables) {
  const lines = {};

  for (const f of linesGeojson.features) {
    const coords = f.geometry.coordinates;
    const cum = [0];
    for (let i = 1; i < coords.length; i++) {
      cum.push(cum[i - 1] + haversineKm(coords[i - 1], coords[i]));
    }
    lines[f.properties.lineId] = {
      id: f.properties.lineId,
      color: f.properties.color,
      mode: f.properties.mode,
      coords,
      cum,
      stationKm: {},
      stationName: {},
      trips: [],
    };
  }

  for (const meta of linesJson.lines) {
    const L = lines[meta.id];
    if (!L) continue;
    L.name = meta.name;
    for (const s of meta.stations) {
      L.stationKm[s.code] = s.distAlong;
      L.stationName[s.code] = s.name;
    }
  }

  const tripIndex = {};
  for (const tt of timetables) {
    const L = lines[tt.lineId];
    if (!L) continue;
    let trips = tt.trips ?? [];
    // format ringkas (BRT): pola berhenti sekali + daftar jam berangkat,
    // dikembangkan jadi trip biasa di sini
    if (tt.compact) {
      trips = tt.compact.flatMap((block) =>
        block.starts.map((t0, i) => ({
          id: `${tt.lineId}-${tt.service}-${block.direction}-${i}`,
          dest: block.dest,
          stops: block.stops.map((o) => ({
            s: o.s,
            a: t0 + o.ao,
            d: t0 + o.do,
          })),
        }))
      );
    }
    L.trips.push(...trips);
    for (const tr of trips) tripIndex[tr.id] = { trip: tr, line: L };
  }

  // km sepanjang jalur -> [lon, lat] + arah derajat (binary search vertex)
  function pointAt(L, km) {
    const { coords, cum } = L;
    const target = Math.max(0, Math.min(km, cum[cum.length - 1]));
    let lo = 0;
    let hi = cum.length - 1;
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      if (cum[mid] <= target) lo = mid;
      else hi = mid;
    }
    const segLen = cum[hi] - cum[lo] || 1e-9;
    const f = (target - cum[lo]) / segLen;
    const [x1, y1, z1 = 0] = coords[lo];
    const [x2, y2, z2 = 0] = coords[hi];
    const lon = x1 + f * (x2 - x1);
    const lat = y1 + f * (y2 - y1);
    const alt = z1 + f * (z2 - z1);
    const bearing =
      (Math.atan2(
        (x2 - x1) * Math.cos((lat * Math.PI) / 180),
        y2 - y1
      ) *
        180) /
      Math.PI;
    return [lon, lat, alt, bearing];
  }

  // posisi semua kendaraan aktif pada detik-simulasi t.
  // Dini hari (t < 04:00) juga dicek sebagai t+24 jam supaya kereta
  // yang jadwalnya melewati tengah malam (detik > 86400) tetap muncul.
  function positionsAt(tRaw) {
    const out = [];
    const candidates = tRaw < 14400 ? [tRaw, tRaw + 86400] : [tRaw];
    for (const L of Object.values(lines)) {
      for (const trip of L.trips) {
        const stops = trip.stops;
        const t = candidates.find(
          (tc) => tc >= stops[0].d && tc <= stops[stops.length - 1].a
        );
        if (t === undefined) continue;

        let km = null;
        let moving = false;
        for (let j = 0; j < stops.length; j++) {
          if (t >= stops[j].a && t <= stops[j].d) {
            km = L.stationKm[stops[j].s]; // berhenti di stasiun
            break;
          }
          if (j + 1 < stops.length && t > stops[j].d && t < stops[j + 1].a) {
            const f = easeInOutCubic(
              (t - stops[j].d) / (stops[j + 1].a - stops[j].d)
            );
            const k1 = L.stationKm[stops[j].s];
            const k2 = L.stationKm[stops[j + 1].s];
            km = k1 + f * (k2 - k1);
            moving = k2 >= k1 ? 1 : -1;
            break;
          }
        }
        if (km === null) continue;

        const [lon, lat, alt, bearing] = pointAt(L, km);
        out.push({
          id: trip.id,
          lineId: L.id,
          color: L.color,
          mode: L.mode,
          dest: L.stationName[trip.dest] ?? trip.dest,
          lngLat: [lon, lat],
          alt,
          // kereta arah balik memakai geometri yang sama tapi mundur
          bearing: moving === -1 ? bearing + 180 : bearing,
          moving: Boolean(moving),
        });
      }
    }
    return out;
  }

  // detail satu kereta (untuk panel info): tujuan + stasiun berikutnya
  function vehicleInfo(id, tRaw) {
    const entry = tripIndex[id];
    if (!entry) return null;
    const { trip, line } = entry;
    const t =
      tRaw < 14400 && trip.stops[0].d > tRaw ? tRaw + 86400 : tRaw;
    const next = trip.stops.find((st) => st.a > t);
    return {
      lineId: line.id,
      dest: line.stationName[trip.dest] ?? trip.dest,
      nextStation: next ? line.stationName[next.s] : null,
    };
  }

  return { positionsAt, vehicleInfo, lines };
}
