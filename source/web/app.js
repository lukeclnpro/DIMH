const $=s=>document.querySelector(s);const $$=s=>document.querySelectorAll(s);
let user=null,path="",authMode="login";

function toast(msg,bad=false){const e=$("#toast");e.textContent=msg;e.className=bad?"show bad":"show";setTimeout(()=>e.className="",2800)}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
function fmtBytes(n){if(!n)return"0 o";const u=["o","Ko","Mo","Go","To"];let i=0,x=n;while(x>=1024&&i<u.length-1){x/=1024;i++}return`${x.toFixed(x>=100?0:x>=10?1:2)} ${u[i]}`}
function fmtTime(sec){let d=Math.floor(sec/86400);sec%=86400;let h=Math.floor(sec/3600);sec%=3600;let m=Math.floor(sec/60);return d?`${d}j ${h}h`:`${h}h ${m}min`}
async function api(url,opt={}){const r=await fetch(url,opt);let data={};try{data=await r.json()}catch{}if(!r.ok)throw Error(data.detail||data.message||`Erreur ${r.status}`);return data}

async function boot(){try{user=await api("/api/auth/me");showApp()}catch(e){showAuth()}}
function showAuth(){ $("#authView").classList.remove("hidden");$("#appView").classList.add("hidden"); setAuthMode("login")}
function showApp(){ $("#authView").classList.add("hidden");$("#appView").classList.remove("hidden");$("#userBadge").textContent=user.public?"Compte public · lecture seule":`Connecté en tant que ${user.username}`;$("#readOnlyNotice").classList.toggle("hidden",!user.public);$("#logoutBtn").classList.toggle("hidden",user.public);$("#publicExitBtn").classList.toggle("hidden",!user.public);$("#updateService").classList.toggle("hidden",user.public);loadDrive()}
function setAuthMode(mode){authMode=mode;$$(".tab").forEach(b=>b.classList.toggle("active",b.dataset.auth===mode));$("#authForm").classList.toggle("hidden",mode==="public");$("#publicEnter").classList.toggle("hidden",mode!=="public");$("#authSubmit").textContent=mode==="register"?"Créer mon compte":"Se connecter";$("#password").autocomplete=mode==="register"?"new-password":"current-password"}
$$(".tab").forEach(b=>b.onclick=()=>setAuthMode(b.dataset.auth));
$("#publicEnter").onclick=async()=>{try{user=await api("/api/auth/public",{method:"POST"});showApp();toast("Compte public ouvert")}catch(err){toast(err.message,true)}};
$("#authForm").onsubmit=async e=>{e.preventDefault();try{const body={username:$("#username").value,password:$("#password").value};user=await api(`/api/auth/${authMode}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});showApp();toast(authMode==="register"?"Compte créé":"Connexion réussie")}catch(err){toast(err.message,true)}};
$("#logoutBtn").onclick=async()=>{await api("/api/auth/logout",{method:"POST"});user=null;path="";showAuth()};
$("#publicExitBtn").onclick=()=>{user=null;path="";showAuth()};
$("#backBtn").onclick=()=>{if(!path)return;const parts=path.split("/").filter(Boolean);parts.pop();path=parts.join("/");loadDrive()};
$("#rootBtn").onclick=()=>{path="";loadDrive()};

function icon(item){if(item.is_dir)return"▰";const ext=(item.extension||"").toLowerCase();if([".jpg",".jpeg",".png",".gif",".webp"].includes(ext))return"▧";if([".mp3",".wav",".ogg",".m4a"].includes(ext))return"♫";if([".mp4",".mkv",".webm",".mov"].includes(ext))return"▶";if([".zip",".rar",".7z"].includes(ext))return"◇";return"□"}
function displayPath(){return path?path.split("/").map(esc).join(" / "):"Racine"}
async function loadDrive(){setSection("drive");$("#breadcrumb").innerHTML=displayPath();clearSelection(true);try{const items=await api(`/api/files?path=${encodeURIComponent(path)}`);renderFiles(items)}catch(e){toast(e.message,true)}}

let currentItems=[];
let selectedPaths=new Set();
let lastClickedIndex=null;
let clipboard=null; // {mode:"copy"|"move", paths:[...]}

function renderFiles(items){
  currentItems=items;
  const g=$("#fileGrid");g.innerHTML="";
  $("#emptyState").classList.toggle("hidden",items.length>0);
  items.forEach((it,idx)=>{
    const isSelected=selectedPaths.has(it.path);
    const isCut=!!(clipboard&&clipboard.mode==="move"&&clipboard.paths.includes(it.path));
    const c=document.createElement("article");
    c.className="file-card"+(isSelected?" selected":"")+(isCut?" cut":"");
    c.innerHTML=`${user.public?"":`<input type="checkbox" class="select-checkbox" ${isSelected?"checked":""}>`}
      ${user.public?"":`<button class="card-menu-btn" type="button" title="Actions">⋮</button>`}
      <div class="file-icon">${icon(it)}</div><div class="file-name" title="${esc(it.name)}">${esc(it.name)}</div><div class="file-meta">${it.is_dir?"Dossier":fmtBytes(it.size)}</div>`;
    if(!user.public){
      c.querySelector(".select-checkbox").onclick=e=>{e.stopPropagation();toggleSelect(it.path,idx)};
      c.querySelector(".card-menu-btn").onclick=e=>{e.stopPropagation();const r=e.currentTarget.getBoundingClientRect();openContextMenu(it,r.left,r.bottom+4)};
      c.oncontextmenu=e=>{e.preventDefault();openContextMenu(it,e.clientX,e.clientY)};
    }
    c.onclick=e=>{
      if(!user.public&&e.shiftKey){selectRange(idx);return}
      if(!user.public&&(e.ctrlKey||e.metaKey)){toggleSelect(it.path,idx);return}
      it.is_dir?(path=path?`${path}/${it.name}`:it.name,loadDrive()):download(it.path);
    };
    g.appendChild(c);
  });
  updateSelectionBar();
}

function toggleSelect(p,idx){
  if(selectedPaths.has(p))selectedPaths.delete(p);else selectedPaths.add(p);
  lastClickedIndex=idx;
  renderFiles(currentItems);
}
function selectRange(idx){
  if(lastClickedIndex===null){toggleSelect(currentItems[idx].path,idx);return}
  const[a,b]=[lastClickedIndex,idx].sort((x,y)=>x-y);
  for(let i=a;i<=b;i++)selectedPaths.add(currentItems[i].path);
  renderFiles(currentItems);
}
function selectAllToggle(){
  if(currentItems.length&&selectedPaths.size===currentItems.length)selectedPaths.clear();
  else currentItems.forEach(it=>selectedPaths.add(it.path));
  renderFiles(currentItems);
}
function clearSelection(skipRender){
  selectedPaths.clear();lastClickedIndex=null;
  if(!skipRender)renderFiles(currentItems);
}
function updateSelectionBar(){
  const n=selectedPaths.size;
  $("#selectionBar").classList.toggle("hidden",n===0);
  $("#selectionCount").textContent=`${n} élément(s) sélectionné(s)`;
  $("#selectionRenameBtn").classList.toggle("hidden",n!==1);
  $("#selectAllBtn").classList.toggle("hidden",user.public||!currentItems.length);
  $("#selectAllBtn").textContent=(currentItems.length&&n===currentItems.length)?"☐ Tout désélectionner":"☑ Tout sélectionner";
  const hasClip=!!(clipboard&&clipboard.paths.length);
  $("#pasteBtn").classList.toggle("hidden",user.public||!hasClip);
  if(hasClip)$("#pasteBtn").textContent=`📋 Coller (${clipboard.paths.length})`;
}

function copySelection(){
  if(!selectedPaths.size)return;
  clipboard={mode:"copy",paths:[...selectedPaths]};
  toast(`${clipboard.paths.length} élément(s) copié(s)`);
  renderFiles(currentItems);
}
function cutSelection(){
  if(!selectedPaths.size)return;
  clipboard={mode:"move",paths:[...selectedPaths]};
  toast(`${clipboard.paths.length} élément(s) coupé(s)`);
  renderFiles(currentItems);
}
let pasteConflictApplyAll=null;
async function pasteClipboard(){
  if(!clipboard||!clipboard.paths.length)return;
  const btn=$("#pasteBtn");btn.disabled=true;
  pasteConflictApplyAll=null;
  const groups={abort:[],rename:[],replace:[]};
  let skipped=0;
  for(const p of clipboard.paths){
    const name=p.split("/").pop();
    try{
      const res=await api(`/api/files/exists?path=${encodeURIComponent(path)}&name=${encodeURIComponent(name)}`);
      if(!res.exists){groups.abort.push(p);continue}
      let action;
      if(pasteConflictApplyAll)action=pasteConflictApplyAll;
      else{const d=await askConflict(name);action=d.action;if(d.applyAll)pasteConflictApplyAll=d.action}
      if(action==="abort"){skipped++;continue}
      groups[action].push(p);
    }catch(e){toast(e.message,true)}
  }
  const endpoint=clipboard.mode==="move"?"/api/files/move":"/api/files/copy";
  let okCount=0,errCount=0;
  for(const[mode,items]of Object.entries(groups)){
    if(!items.length)continue;
    try{
      const results=await api(`${endpoint}?destination=${encodeURIComponent(path)}&on_conflict=${mode}`,{
        method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({paths:items})
      });
      results.forEach(r=>r.ok?okCount++:errCount++);
    }catch(e){errCount+=items.length;toast(e.message,true)}
  }
  btn.disabled=false;
  if(clipboard.mode==="move")clipboard=null;
  toast(`${okCount} élément(s) collé(s)${errCount?`, ${errCount} erreur(s)`:""}${skipped?`, ${skipped} ignoré(s)`:""}`,errCount>0);
  clearSelection(true);loadDrive();
}
async function deleteSelection(){
  if(!selectedPaths.size)return;
  if(!confirm(`Déplacer ${selectedPaths.size} élément(s) vers la corbeille ?`))return;
  try{
    const results=await api("/api/files/delete-batch",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({paths:[...selectedPaths]})});
    const errs=results.filter(r=>!r.ok).length;
    toast(errs?`Supprimé avec ${errs} erreur(s)`:"Éléments déplacés vers la corbeille",errs>0);
  }catch(e){toast(e.message,true)}
  clearSelection(true);loadDrive();
}
function downloadSelection(){
  const files=[...selectedPaths].map(p=>currentItems.find(i=>i.path===p)).filter(it=>it&&!it.is_dir);
  if(!files.length)return toast("Sélectionnez au moins un fichier (le téléchargement groupé de dossiers n'est pas encore disponible)",true);
  files.forEach((it,i)=>setTimeout(()=>download(it.path),i*350));
}
async function renameSelected(){
  if(selectedPaths.size!==1)return;
  const p=[...selectedPaths][0];
  const it=currentItems.find(i=>i.path===p);if(!it)return;
  const newName=prompt("Nouveau nom",it.name);
  if(!newName||newName===it.name)return;
  try{
    await api(`/api/files/rename?path=${encodeURIComponent(p)}&new_name=${encodeURIComponent(newName)}`,{method:"POST"});
    clearSelection(true);loadDrive();
  }catch(e){toast(e.message,true)}
}

/* Menu contextuel (clic droit sur desktop, bouton ⋮ partout, y compris mobile) */
function openContextMenu(it,x,y){
  if(!selectedPaths.has(it.path)){selectedPaths=new Set([it.path]);lastClickedIndex=currentItems.findIndex(i=>i.path===it.path);renderFiles(currentItems)}
  const multi=selectedPaths.size>1;
  const rows=[];
  if(!multi&&it.is_dir)rows.push(`<button data-act="open">Ouvrir</button>`);
  if(!multi&&!it.is_dir)rows.push(`<button data-act="download">Télécharger</button>`);
  if(!multi)rows.push(`<button data-act="rename">Renommer</button>`);
  rows.push(`<button data-act="copy">Copier</button>`,`<button data-act="cut">Couper</button>`,`<hr>`,`<button data-act="delete" class="danger">Supprimer</button>`);
  const menu=$("#contextMenu");
  menu.innerHTML=rows.join("");
  menu.querySelectorAll("button").forEach(b=>b.onclick=()=>{
    const act=b.dataset.act;closeContextMenu();
    if(act==="open"){path=path?`${path}/${it.name}`:it.name;loadDrive()}
    else if(act==="download")download(it.path);
    else if(act==="rename")renameSelected();
    else if(act==="copy")copySelection();
    else if(act==="cut")cutSelection();
    else if(act==="delete")deleteSelection();
  });
  menu.classList.add("open");
  const rect=menu.getBoundingClientRect();
  menu.style.left=Math.max(4,Math.min(x,window.innerWidth-rect.width-8))+"px";
  menu.style.top=Math.max(4,Math.min(y,window.innerHeight-rect.height-8))+"px";
}
function closeContextMenu(){$("#contextMenu").classList.remove("open")}
document.addEventListener("click",e=>{if(!e.target.closest("#contextMenu")&&!e.target.closest(".card-menu-btn"))closeContextMenu()});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeContextMenu()});

$("#selectAllBtn").onclick=selectAllToggle;
$("#pasteBtn").onclick=pasteClipboard;
$("#selectionDownloadBtn").onclick=downloadSelection;
$("#selectionCopyBtn").onclick=copySelection;
$("#selectionCutBtn").onclick=cutSelection;
$("#selectionRenameBtn").onclick=renameSelected;
$("#selectionDeleteBtn").onclick=deleteSelection;
$("#selectionClearBtn").onclick=()=>clearSelection();

async function download(p){window.open(`/api/files/download?path=${encodeURIComponent(user.public?p:p.replace(user.username+"/",""))}`,"_blank")}
$("#refreshBtn").onclick=loadDrive;
$("#uploadBtn").onclick=()=>user.public?toast("Le compte public est en lecture seule",true):$("#fileInput").click();
$("#fileInput").onchange=e=>{handleFiles(e.target.files);e.target.value=""};

/* ---------- Upload avancé : file d'attente, progression, vitesse, doublons ---------- */
let uploadQueue=[];
let uploadActiveSlots=0;
const UPLOAD_MAX_PARALLEL=3;
let conflictApplyAllAction=null; // 'replace' | 'rename' | 'abort' une fois "appliquer à tous" coché
let uploadPanelCollapsed=false;

function fmtSpeed(bytesPerSec){return bytesPerSec>0?`${fmtBytes(bytesPerSec)}/s`:"—"}
function fmtEta(remainingBytes,speed){
  if(!(speed>0))return"…";
  let sec=Math.ceil(remainingBytes/speed);
  if(sec<1)return"< 1 s";
  const m=Math.floor(sec/60),s=sec%60;
  return m?`${m} min ${s}s restantes`:`${s}s restantes`;
}

function handleFiles(fileList){
  const files=[...fileList];
  if(!files.length)return;
  const items=files.map(f=>({
    id:`${Date.now()}_${Math.random().toString(36).slice(2)}`,
    file:f,status:"queued",loaded:0,total:f.size,speed:0,error:"",conflict:null,
    startTime:0,lastTick:0,lastLoaded:0,xhr:null
  }));
  uploadQueue.push(...items);
  showUploadPanel();
  renderUploadPanel();
  processConflictsThenUpload(items);
}

async function processConflictsThenUpload(items){
  for(const item of items){
    if(item.status==="canceled")continue;
    await resolveConflict(item);
    if(item.status!=="canceled")queueUploadWorker(item);
    else maybeFinishUploads();
  }
}

async function resolveConflict(item){
  item.status="checking";renderUploadPanel();
  try{
    const res=await api(`/api/files/exists?path=${encodeURIComponent(path)}&name=${encodeURIComponent(item.file.name)}`);
    if(!res.exists){item.status="queued";return}
    let action,applyAll=false;
    if(conflictApplyAllAction){action=conflictApplyAllAction}
    else{const decision=await askConflict(item.file.name);action=decision.action;applyAll=decision.applyAll}
    item.conflict=action;
    if(applyAll)conflictApplyAllAction=action;
    if(action==="abort"){item.status="canceled";item.error="Ignoré (doublon)"}
    else item.status="queued";
  }catch(e){item.status="error";item.error=e.message}
  renderUploadPanel();
}

function askConflict(name){
  return new Promise(resolve=>{
    $("#conflictMessage").textContent=`Un fichier nommé « ${name} » existe déjà dans ce dossier.`;
    $("#conflictApplyAll").checked=false;
    $("#conflictDialog").showModal();
    const finish=action=>{
      $("#conflictCancel").onclick=null;$("#conflictKeepBoth").onclick=null;$("#conflictReplace").onclick=null;
      $("#conflictDialog").close();
      resolve({action,applyAll:$("#conflictApplyAll").checked});
    };
    $("#conflictCancel").onclick=()=>finish("abort");
    $("#conflictKeepBoth").onclick=()=>finish("rename");
    $("#conflictReplace").onclick=()=>finish("replace");
  });
}

function queueUploadWorker(item){
  const tryStart=()=>{
    if(uploadActiveSlots>=UPLOAD_MAX_PARALLEL){setTimeout(tryStart,150);return}
    uploadActiveSlots++;
    uploadOne(item).finally(()=>{uploadActiveSlots--;maybeFinishUploads()});
  };
  tryStart();
}

function uploadOne(item){
  return new Promise(resolve=>{
    item.status="uploading";item.loaded=0;item.startTime=performance.now();item.lastTick=item.startTime;item.lastLoaded=0;
    renderUploadPanel();
    const fd=new FormData();fd.append("file",item.file);
    const xhr=new XMLHttpRequest();item.xhr=xhr;
    const qs=`path=${encodeURIComponent(path)}&on_conflict=${encodeURIComponent(item.conflict||"abort")}`;
    xhr.open("POST",`/api/files/upload?${qs}`);
    xhr.upload.onprogress=e=>{
      if(!e.lengthComputable)return;
      const now=performance.now(),dt=(now-item.lastTick)/1000;
      if(dt>0.2){item.speed=(e.loaded-item.lastLoaded)/dt;item.lastTick=now;item.lastLoaded=e.loaded}
      item.loaded=e.loaded;item.total=e.total;
      renderUploadPanel();
    };
    xhr.onload=()=>{
      if(xhr.status>=200&&xhr.status<300){item.status="done";item.loaded=item.total;item.speed=0}
      else{let msg=`Erreur ${xhr.status}`;try{msg=JSON.parse(xhr.responseText).detail||msg}catch{}item.status="error";item.error=msg}
      renderUploadPanel();resolve();
    };
    xhr.onerror=()=>{item.status="error";item.error="Erreur réseau";renderUploadPanel();resolve()};
    xhr.onabort=()=>{item.status="canceled";item.error="Annulé";renderUploadPanel();resolve()};
    xhr.send(fd);
  });
}

function cancelUpload(id){
  const item=uploadQueue.find(i=>i.id===id);if(!item)return;
  if(item.status==="uploading"&&item.xhr)item.xhr.abort();
  else if(item.status==="queued"||item.status==="checking"){item.status="canceled";item.error="Annulé";renderUploadPanel();maybeFinishUploads()}
}

function retryUpload(id){
  const item=uploadQueue.find(i=>i.id===id);if(!item)return;
  item.status="queued";item.error="";item.loaded=0;item.speed=0;
  renderUploadPanel();
  resolveConflict(item).then(()=>{if(item.status!=="canceled")queueUploadWorker(item)});
}

function cancelAllUploads(){
  uploadQueue.forEach(item=>{
    if(item.status==="uploading"&&item.xhr)item.xhr.abort();
    else if(item.status==="queued"||item.status==="checking"){item.status="canceled";item.error="Annulé"}
  });
  renderUploadPanel();
}

let uploadsFinishedHandled=true;
function maybeFinishUploads(){
  const settled=["done","error","canceled"];
  const allSettled=uploadQueue.every(i=>settled.includes(i.status));
  renderUploadPanel();
  if(allSettled&&!uploadsFinishedHandled){
    uploadsFinishedHandled=true;
    loadDrive();
    const hasError=uploadQueue.some(i=>i.status==="error");
    if(!hasError)setTimeout(()=>{if(uploadQueue.every(i=>settled.includes(i.status)))hideUploadPanel()},2200);
  }
}

function showUploadPanel(){uploadsFinishedHandled=false;$("#uploadPanel").classList.remove("hidden")}
function hideUploadPanel(){$("#uploadPanel").classList.add("hidden");uploadQueue=[];conflictApplyAllAction=null;renderUploadPanel()}
$("#uploadPanelClose").onclick=()=>{
  const stillActive=uploadQueue.some(i=>["queued","checking","uploading"].includes(i.status));
  if(stillActive&&!confirm("Des imports sont en cours. Les annuler et fermer ?"))return;
  cancelAllUploads();hideUploadPanel();
};
$("#uploadPanelToggle").onclick=()=>{uploadPanelCollapsed=!uploadPanelCollapsed;$("#uploadPanel").classList.toggle("collapsed",uploadPanelCollapsed);$("#uploadPanelToggle").textContent=uploadPanelCollapsed?"+":"–"};

function statusLabel(item){
  switch(item.status){
    case"checking":return"Vérification…";
    case"queued":return"En attente";
    case"uploading":return`${Math.floor(item.total?item.loaded/item.total*100:0)}%`;
    case"done":return"Terminé";
    case"error":return item.error||"Erreur";
    case"canceled":return item.error||"Annulé";
    default:return"";
  }
}
function renderUploadPanel(){
  if(!uploadQueue.length)return;
  const done=uploadQueue.filter(i=>i.status==="done").length;
  const errors=uploadQueue.filter(i=>i.status==="error").length;
  const totalLoaded=uploadQueue.reduce((a,i)=>a+(i.status==="done"?i.total:i.loaded),0);
  const totalSize=uploadQueue.reduce((a,i)=>a+i.total,0);
  const pct=totalSize?Math.floor(totalLoaded/totalSize*100):0;
  const active=uploadQueue.some(i=>["queued","checking","uploading"].includes(i.status));
  $("#uploadPanelTitle").textContent=active?`Import… (${done}/${uploadQueue.length})`:errors?`Import terminé avec erreurs`:`Import terminé (${done}/${uploadQueue.length})`;
  $("#uploadPanelSummary").innerHTML=`<div>${done}/${uploadQueue.length} fichier(s) importé(s)${errors?` · ${errors} en erreur`:""}</div><div class="bar"><i style="width:${pct}%"></i></div>`;
  $("#uploadPanelList").innerHTML=uploadQueue.map(item=>{
    const pctItem=item.total?Math.floor(item.loaded/item.total*100):0;
    const meta=item.status==="uploading"?`${fmtBytes(item.loaded)} / ${fmtBytes(item.total)} · ${fmtSpeed(item.speed)} · ${fmtEta(item.total-item.loaded,item.speed)}`:item.status==="done"?fmtBytes(item.total):"";
    let actions="";
    if(item.status==="uploading"||item.status==="queued"||item.status==="checking")actions=`<button class="danger" onclick="cancelUpload('${item.id}')">Annuler</button>`;
    else if(item.status==="error")actions=`<button onclick="retryUpload('${item.id}')">Réessayer</button>`;
    return`<div class="upload-row ${item.status}">
      <div class="upload-row-top"><span class="upload-name" title="${esc(item.file.name)}">${esc(item.file.name)}</span><span class="upload-status ${item.status}">${esc(statusLabel(item))}</span></div>
      <div class="bar"><i style="width:${item.status==="done"?100:pctItem}%"></i></div>
      <div class="upload-row-meta"><small>${esc(meta)}</small><div class="upload-row-actions">${actions}</div></div>
    </div>`;
  }).join("");
}
$("#newFolderBtn").onclick=async()=>{if(user.public)return toast("Le compte public est en lecture seule",true);const name=prompt("Nom du dossier");if(!name)return;try{await api(`/api/files/folder?path=${encodeURIComponent(path)}&name=${encodeURIComponent(name)}`,{method:"POST"});loadDrive()}catch(e){toast(e.message,true)}};
$("#newFileBtn").onclick=()=>{if(user.public)return toast("Le compte public est en lecture seule",true);$("#textDialog").showModal()};
$("#saveText").onclick=async e=>{e.preventDefault();try{await api(`/api/files/text?path=${encodeURIComponent(path)}&name=${encodeURIComponent($("#textName").value)}&content=${encodeURIComponent($("#textContent").value)}`,{method:"POST"});$("#textDialog").close();$("#textName").value="";$("#textContent").value="";loadDrive()}catch(err){toast(err.message,true)}};

$$(".nav-item[data-section]").forEach(b=>b.onclick=()=>setSection(b.dataset.section));
function setSection(s){$$(".nav-item[data-section]").forEach(b=>b.classList.toggle("active",b.dataset.section===s));$("#driveSection").classList.toggle("hidden",s!=="drive");$("#sharedSection").classList.toggle("hidden",s!=="shared");$("#performanceSection").classList.toggle("hidden",s!=="performance");$("#pageTitle").textContent=s==="drive"?"Mon Drive":s==="shared"?"Partages":"Performances serveur";if(s==="shared")loadShared();if(s==="performance")loadStats()}

let pickerPath="";
let selectedSendPath="";

function pickerDisplayPath(){
  return pickerPath ? pickerPath.split("/").map(esc).join(" / ") : "Racine";
}
async function loadPicker(){
  $("#pickerBreadcrumb").innerHTML=pickerDisplayPath();
  try{
    const items=await api(`/api/files?path=${encodeURIComponent(pickerPath)}`);
    const g=$("#pickerGrid"); g.innerHTML="";
    items.forEach(it=>{
      const c=document.createElement("article");
      c.className="file-card";
      c.innerHTML=`<div class="file-icon">${icon(it)}</div><div class="file-name" title="${esc(it.name)}">${esc(it.name)}</div><div class="file-meta">${it.is_dir?"Dossier":fmtBytes(it.size)}</div>`;
      c.onclick=()=>{
        if(it.is_dir){
          pickerPath=pickerPath?`${pickerPath}/${it.name}`:it.name;
          loadPicker();
        }else{
          selectedSendPath=it.path;
          $("#selectedFileLabel").textContent=`Sélectionné : ${it.name}`;
          $("#confirmSendFile").disabled=false;
          g.querySelectorAll(".file-card").forEach(x=>x.classList.remove("selected"));
          c.classList.add("selected");
        }
      };
      g.appendChild(c);
    });
    if(!items.length) g.innerHTML="<p class='muted'>Dossier vide.</p>";
  }catch(e){toast(e.message,true)}
}
async function loadSendUsers(){
  const select=$("#sendUsername");
  select.innerHTML='<option value="">Chargement des comptes…</option>';
  try{
    const users=await api("/api/shares/users");
    select.innerHTML=users.length
      ? '<option value="">Sélectionnez une personne…</option>'+users.map(u=>`<option value="${esc(u.username)}">${esc(u.username)}</option>`).join("")
      : '<option value="">Aucun autre compte disponible</option>';
    select.disabled=!users.length;
  }catch(e){
    select.innerHTML='<option value="">Impossible de charger les comptes</option>';
    select.disabled=true;
    toast(e.message,true);
  }
}
function openSendPicker(){
  if(user.public)return toast("Le compte public est en lecture seule",true);
  pickerPath=""; selectedSendPath="";
  $("#sendUsername").value="";
  $("#sendUsername").disabled=false;
  $("#sendPermission").value="read";
  $("#selectedFileLabel").textContent="Aucun fichier sélectionné";
  $("#confirmSendFile").disabled=true;
  $("#sendFileDialog").showModal();
  loadPicker();
  loadSendUsers();
}
$("#sendFileBtn").onclick=openSendPicker;
$("#closeSendFile").onclick=()=>$("#sendFileDialog").close();
$("#pickerBack").onclick=()=>{
  if(!pickerPath)return;
  const parts=pickerPath.split("/").filter(Boolean); parts.pop(); pickerPath=parts.join("/");
  loadPicker();
};
$("#pickerRoot").onclick=()=>{pickerPath="";loadPicker()};
$("#confirmSendFile").onclick=async()=>{
  const username=$("#sendUsername").value.trim();
  if(!selectedSendPath)return toast("Sélectionnez un fichier",true);
  if(!username)return toast("Indiquez le nom de l'utilisateur destinataire",true);
  const b=$("#confirmSendFile"); b.disabled=true; b.textContent="Envoi…";
  try{
    const out=await api(`/api/shares/user?path=${encodeURIComponent(selectedSendPath)}`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({username,permission:$("#sendPermission").value})
    });
    $("#sendFileDialog").close();
    toast(`Fichier envoyé à ${out.user}`);
    loadShared();
  }catch(e){toast(e.message,true)}
  finally{b.disabled=false;b.textContent="Envoyer le fichier"}
};

async function loadShared(){try{const rows=await api("/api/shares/mine");$("#sharedList").innerHTML=rows.length?rows.map(r=>`<div class="list-row"><div><div class="name">${esc(r.path.split(/[\\/]/).pop())}</div><small>Partagé par ${esc(r.owner)} · ${esc(r.permission)}</small></div><button class="secondary" onclick="download('__share__/${esc(r.token)}')">Télécharger</button></div>`).join(""):"<p class='muted'>Aucun partage reçu.</p>"}catch(e){toast(e.message,true)}}
async function loadStats(){try{const s=await api("/api/system/stats");$("#cpuStat").textContent=`${s.cpu}%`;$("#cpuBar").style.width=s.cpu+"%";$("#ramStat").textContent=`${s.ram_percent}%`;$("#ramBar").style.width=s.ram_percent+"%";$("#ramMeta").textContent=`${fmtBytes(s.ram_used)} / ${fmtBytes(s.ram_total)}`;$("#diskStat").textContent=`${s.drive_percent}%`;$("#diskBar").style.width=s.drive_percent+"%";$("#diskMeta").textContent=`Drive : ${fmtBytes(s.drive_used)} / ${fmtBytes(s.drive_total)}`;$("#cpuMeta").textContent=`Charge instantanée`;$("#hostMeta").textContent=s.hostname;$("#uptimeStat").textContent=fmtTime(s.uptime)}catch(e){toast(e.message,true)}}
$("#runBenchmark").onclick=async()=>{const b=$("#runBenchmark");b.disabled=true;b.textContent="Test en cours…";try{const w=await api("/api/system/disk-benchmark?size_mb=64",{method:"POST"});$("#writeStat").textContent=`${w.write_mbps} Mo/s`;$("#writeBar").style.width=Math.min(100,w.write_mbps/5)+"%";$("#writeMeta").textContent=`${w.size_mb} Mo écrits puis supprimés`;const size=16*1024*1024,t0=performance.now();const r=await fetch(`/api/system/download-test?size=${size}`);await r.arrayBuffer();const down=size/((performance.now()-t0)/1000)/1024/1024;$("#netStat").textContent=`${down.toFixed(1)} Mb/s`;$("#netBar").style.width=Math.min(100,down/10)+"%";$("#netMeta").textContent="Téléchargement navigateur → serveur";loadStats();toast("Benchmark terminé")}catch(e){toast(e.message,true)}finally{b.disabled=false;b.textContent="Tester les performances"}};
$("#updateService").onclick=async()=>{const b=$("#updateService");if(user.public)return toast("Le compte public ne peut pas mettre à jour HomeDrive",true);if(!confirm("Mettre à jour HomeDrive depuis le dépôt GitHub ?"))return;b.disabled=true;b.textContent="Mise à jour…";try{const result=await api("/api/system/update",{method:"POST"});toast(result.message||"HomeDrive mis à jour");}catch(e){toast(e.message,true)}finally{b.disabled=false;b.textContent="Mettre à jour"}};
$("#searchInput").oninput=async e=>{const q=e.target.value.trim();if(!q){$("#searchResults").classList.add("hidden");return}try{const rows=await api(`/api/search?q=${encodeURIComponent(q)}`);$("#searchResults").classList.remove("hidden");$("#searchResults").innerHTML=rows.map(x=>`<div class="list-row"><div class="name">${icon(x)} ${esc(x.name)}</div><button class="secondary" onclick="download('${esc(x.path)}')">Ouvrir</button></div>`).join("")||"<p class='muted'>Aucun résultat.</p>"}catch(err){toast(err.message,true)}};

boot();
