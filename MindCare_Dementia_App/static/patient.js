const $ = id => document.getElementById(id);
let pid = null;
const icons = { sequence: "🎨", missing_object: "🔎", association: "🧩", recognition: "🖼️" };
const desc = {
  sequence: "Remember and repeat colors in order.",
  missing_object: "Find the object that disappeared.",
  association: "Match related pictures.",
  recognition: "Remember pictures and recognize them.",
};

async function api(url, opt = {}) {
  const r = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opt });
  const d = await r.json();
  if (!r.ok) throw Error(d.error || "Request failed");
  return d;
}

async function showGames(patient) {
  pid = patient.id;
  sessionStorage.setItem("mindcarePatient", String(pid));
  sessionStorage.setItem("mindcarePatientCode", patient.patient_code);
  $("dash").hidden = false;
  $("welcome").textContent = "Hello " + (patient.full_name || patient.patient_code) + ". Choose a game.";
  const g = await api("/api/games?patient_id=" + pid);
  $("games").innerHTML = g.map(x => `
    <article class="card">
      <div class="emoji">${icons[x.game_key]}</div>
      <h3>${x.game_name}</h3>
      <p>${desc[x.game_key]}</p>
      <p>Current level: <b>${x.current_level}</b></p>
      <a href="/play/${x.game_key}"><button>Play game</button></a>
    </article>`).join("");
}

$("login").onsubmit = async e => {
  e.preventDefault();
  $("msg").textContent = "";
  try {
    const patient = await api("/api/patient/login", {
      method: "POST",
      body: JSON.stringify({ patient_code: $("patient_code").value.trim() }),
    });
    await showGames(patient);
  } catch (err) {
    $("msg").textContent = err.message;
    $("dash").hidden = true;
  }
};

const saved = sessionStorage.getItem("mindcarePatientCode");
if (saved) {
  $("patient_code").value = saved;
  api("/api/patient/login", { method: "POST", body: JSON.stringify({ patient_code: saved }) })
    .then(showGames)
    .catch(() => {});
}
