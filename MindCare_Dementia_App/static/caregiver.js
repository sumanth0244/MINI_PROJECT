const $ = id => document.getElementById(id);
let pid = null;

async function api(url, opt = {}) {
  const r = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opt });
  const d = await r.json();
  if (!r.ok) throw Error(d.error || "Request failed");
  return d;
}

function when(value) {
  if (!value) return "—";
  return String(value).replace("T", " ").slice(0, 19);
}

async function loadPatients() {
  const p = await api("/api/patients");
  $("patient").innerHTML = '<option value="">Select patient</option>' + p.map(x =>
    `<option value="${x.id}">${x.full_name} (${x.patient_code})</option>`
  ).join("");
  $("list").innerHTML = `
    <table>
      <tr><th>Patient ID</th><th>Name</th><th>Email</th><th>Sessions</th><th>Average accuracy</th></tr>
      ${p.map(x => `<tr>
        <td>${x.patient_code}</td>
        <td>${x.full_name}</td>
        <td>${x.email || "—"}</td>
        <td>${x.sessions}</td>
        <td>${x.average_accuracy == null ? "—" : x.average_accuracy + "%"}</td>
      </tr>`).join("") || "<tr><td colspan='5'>No patients registered yet.</td></tr>"}
    </table>`;
}

$("add").onsubmit = async e => {
  e.preventDefault();
  const d = Object.fromEntries(new FormData(e.target));
  try {
    const x = await api("/api/patients", { method: "POST", body: JSON.stringify(d) });
    $("msg").textContent = "Patient registered. They can play using Patient ID " + x.patient_code + ".";
    await loadPatients();
    $("patient").value = x.id;
    e.target.reset();
  } catch (err) {
    $("msg").textContent = err.message;
  }
};

$("load").onclick = async () => {
  pid = $("patient").value;
  if (!pid) return alert("Select a patient first");
  $("dash").hidden = false;
  const p = await api("/api/progress/" + pid);
  $("welcome").textContent = "Results for " + p.patient.full_name + " (" + p.patient.patient_code + ")";
  const sessions = p.sessions && p.sessions.length
    ? p.sessions.map(x => `<tr>
        <td>${when(x.created_at)}</td>
        <td>${x.game_name}</td>
        <td>${x.difficulty}</td>
        <td>${x.correct_answers}/${x.total_questions}</td>
        <td>${x.accuracy}%</td>
        <td>${x.reaction_time}s</td>
      </tr>`).join("")
    : "<tr><td colspan='6'>No game results yet. The patient can play from the patient window.</td></tr>";
  $("progress").innerHTML = `
    <p>Email: <b>${p.patient.email || "—"}</b></p>
    <div class="tablewrap">
      <table>
        <tr><th>Game</th><th>Sessions</th><th>Average accuracy</th><th>Current level</th></tr>
        ${p.games.map(x => `<tr>
          <td>${x.game_name}</td>
          <td>${x.sessions}</td>
          <td>${x.average_accuracy == null ? "—" : x.average_accuracy + "%"}</td>
          <td>${x.current_level}</td>
        </tr>`).join("")}
      </table>
    </div>
    <h3>Saved game results</h3>
    <div class="tablewrap">
      <table>
        <tr><th>When</th><th>Game</th><th>Level</th><th>Score</th><th>Accuracy</th><th>Time</th></tr>
        ${sessions}
      </table>
    </div>
    <h3>Recent agent decisions</h3>
    <div class="tablewrap">
      <table>
        <tr><th>Game</th><th>Level</th><th>Decision</th><th>Reason</th></tr>
        ${p.decisions.map(x => `<tr>
          <td>${x.game_name}</td>
          <td>${x.previous_level} → ${x.recommended_level}</td>
          <td>${x.decision}</td>
          <td>${x.reason}</td>
        </tr>`).join("") || "<tr><td colspan='4'>No decisions yet.</td></tr>"}
      </table>
    </div>`;
};

loadPatients().catch(e => {
  $("patient").innerHTML = `<option>${e.message}</option>`;
});
