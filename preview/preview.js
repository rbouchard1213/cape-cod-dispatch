/* Busy Bees preview — the only JS on the site, kept deliberately small:
   1) carry the visitor's picks from screen to screen in the address bar,
   2) echo those picks into headings and the review summary,
   3) the square-foot calculator, the tap-box measuring grid, and the
      cubic-yard helper on the size screens.
   Nothing is sent anywhere — this is a pretend test version. */
(function(){
  var P = new URLSearchParams(location.search);

  /* Echo: <span data-echo="t"></span> shows the value of ?t=... */
  document.querySelectorAll("[data-echo]").forEach(function(el){
    var v = P.get(el.getAttribute("data-echo"));
    if(v){ el.textContent = v; }
  });

  /* Carry: links with data-carry get any picks they don't already have. */
  document.querySelectorAll("a[data-carry]").forEach(function(a){
    var href = a.getAttribute("href");
    var qi = href.indexOf("?");
    var have = new URLSearchParams(qi >= 0 ? href.slice(qi + 1) : "");
    var changed = false;
    P.forEach(function(v, k){
      if(!have.has(k)){ have.set(k, v); changed = true; }
    });
    if(changed){
      a.setAttribute("href", (qi >= 0 ? href.slice(0, qi) : href) + "?" + have.toString());
    }
  });

  /* Details form: pass the picks through as hidden fields, and pre-fill
     the notes box from a "Something else" description. */
  var form = document.getElementById("detailsForm");
  if(form){
    ["t","c","j","v","p","f"].forEach(function(k){
      var v = P.get(k);
      if(v){
        var inp = document.createElement("input");
        inp.type = "hidden"; inp.name = k; inp.value = v;
        form.appendChild(inp);
      }
    });
    var desc = P.get("desc");
    var notes = document.getElementById("fNotes");
    if(desc && notes && !notes.value){ notes.value = desc; }
  }

  /* Back buttons: use real browser history when there is any. */
  document.querySelectorAll("a.js-back").forEach(function(a){
    a.addEventListener("click", function(e){
      if(window.history.length > 1){ e.preventDefault(); window.history.back(); }
    });
  });

  /* ---- Size helpers ---- */
  var LAWN = ["Tiny","Small","Standard","Large","Huge"];
  function lawnTier(sqft){
    if(sqft <= 2000) return 0; if(sqft <= 5000) return 1;
    if(sqft <= 10000) return 2; if(sqft <= 20000) return 3; return 4;
  }
  var MULCH = ["Tiny","Small","Standard","Full","Huge"];
  function mulchTier(yd){
    if(yd <= 1) return 0; if(yd <= 2) return 1;
    if(yd <= 5) return 2; if(yd <= 10) return 3; return 4;
  }
  function fmt(n){ return n.toLocaleString("en-US"); }

  /* Any "use this size" link starts life pointing at the next screen with
     no size picked; the helpers below fill in ?p= as the visitor measures. */
  function setUse(link, label){
    if(!link) return;
    var href = link.getAttribute("href");
    var qi = href.indexOf("?");
    var q = new URLSearchParams(qi >= 0 ? href.slice(qi + 1) : "");
    q.set("p", label);
    link.setAttribute("href", (qi >= 0 ? href.slice(0, qi) : href) + "?" + q.toString());
    link.style.display = "block";
  }

  /* Square-foot calculator: length × width */
  var calcBtn = document.getElementById("calcBtn");
  if(calcBtn){
    calcBtn.addEventListener("click", function(){
      var L = parseFloat(document.getElementById("calcL").value);
      var W = parseFloat(document.getElementById("calcW").value);
      var out = document.getElementById("calcOut");
      if(isNaN(L) || isNaN(W) || L <= 0 || W <= 0){
        out.textContent = "Type both a length and a width, in feet.";
        return;
      }
      var sqft = Math.round(L * W);
      var tier = LAWN[lawnTier(sqft)];
      out.innerHTML = fmt(sqft) + " sq ft &rarr; that&rsquo;s the <span class='tier'>" +
        tier + "</span> size.";
      setUse(document.getElementById("calcUse"),
        tier + " lawn (" + fmt(sqft) + " sq ft, calculator)");
    });
  }

  /* Tap-box grid: each square stands for about 400 sq ft. */
  var grid = document.getElementById("mapGrid");
  if(grid){
    var out = document.getElementById("mapOut");
    var count = 0;
    grid.querySelectorAll("button").forEach(function(b){
      b.addEventListener("click", function(){
        b.classList.toggle("sel");
        count = grid.querySelectorAll("button.sel").length;
        var sqft = count * 400;
        if(count === 0){
          out.textContent = "Tap the squares that cover the area that needs work.";
          return;
        }
        var tier = LAWN[lawnTier(sqft)];
        out.innerHTML = "About " + fmt(sqft) + " sq ft &rarr; that&rsquo;s the <span class='tier'>" +
          tier + "</span> size.";
        setUse(document.getElementById("mapUse"),
          tier + " lawn (about " + fmt(sqft) + " sq ft, tap-box map)");
      });
    });
  }

  /* ---- Progress saving: everything a visitor types is kept on this
     device, in a bucket keyed to who they are. The key is the review
     code the gate stored when they agreed (bb_code) — the code acts as
     a temporary sign-in. Before the gate, or with no code, drafts land
     in a shared GUEST bucket. Different code = different bucket, so
     people sharing a device never see each other's work. ---- */
  function bbBucket(){
    try{
      var c = (localStorage.getItem("bb_code") || "").toUpperCase().replace(/[^A-Z0-9-]/g, "");
      return c || "GUEST";
    }catch(e){ return "GUEST"; }
  }
  function draftKey(scope){ return "bb_draft_v1:" + bbBucket() + ":" + scope; }
  function readDraft(scope){
    try{ var d = JSON.parse(localStorage.getItem(draftKey(scope)) || "null"); return (d && typeof d === "object") ? d : null; }
    catch(e){ return null; }
  }
  function writeDraft(scope, data){
    try{ data.savedAt = new Date().toISOString(); localStorage.setItem(draftKey(scope), JSON.stringify(data)); }catch(e){}
  }
  function clearDraft(scope){ try{ localStorage.removeItem(draftKey(scope)); }catch(e){} }

  /* Small floating "Saved" pill, shown only on pages with a draft form. */
  var saveBar = null, saveBarTimer = null;
  function showSaveBar(text, sticky){
    if(!saveBar){
      saveBar = document.createElement("div");
      saveBar.setAttribute("style", "position:fixed;left:50%;bottom:14px;transform:translateX(-50%);background:#14161F;color:#F7F3EA;font:600 13px/1.3 Inter,system-ui,sans-serif;padding:8px 14px;border-radius:999px;box-shadow:0 4px 14px rgba(0,0,0,.28);z-index:60;opacity:0;transition:opacity .25s;pointer-events:none;max-width:92vw;text-align:center");
      document.body.appendChild(saveBar);
    }
    saveBar.textContent = text;
    saveBar.style.opacity = "1";
    if(saveBarTimer){ clearTimeout(saveBarTimer); saveBarTimer = null; }
    if(!sticky){ saveBarTimer = setTimeout(function(){ saveBar.style.opacity = "0"; }, 3400); }
  }
  function savedTime(iso){
    try{ var d = new Date(iso); if(!isNaN(d)){ return d.toLocaleTimeString("en-US", {hour: "numeric", minute: "2-digit"}); } }catch(e){}
    return "";
  }

  /* ---- Draft forms: any <form data-draft="scope"> auto-saves its named
     fields as you type and restores them on return. ---- */
  document.querySelectorAll("form[data-draft]").forEach(function(form){
    var scope = form.getAttribute("data-draft");
    var fields = Array.prototype.slice.call(form.querySelectorAll("input[name], textarea[name], select[name]"))
      .filter(function(el){ return el.type !== "hidden" && el.type !== "submit"; });
    if(!fields.length) return;
    var draft = readDraft(scope);
    var restored = false;
    if(draft && draft.fields){
      fields.forEach(function(el){
        if(el.value) return; /* a value already here (e.g. carried in the address bar) wins */
        var v = draft.fields[el.name];
        if(v == null || v === "") return;
        /* The contractor-notes box only restores for the same job it was
           written for — your name/address/contact always come back. */
        if(el.name === "notes" && draft.job && P.get("j") && draft.job !== P.get("j")) return;
        el.value = v; restored = true;
      });
    }
    if(restored){ showSaveBar("Restored your draft from earlier on this device" + (draft.savedAt ? " — saved " + savedTime(draft.savedAt) : "") + "."); }
    var t = null;
    function save(flash){
      var data = { fields: {}, job: P.get("j") || (draft && draft.job) || "" };
      fields.forEach(function(el){ data.fields[el.name] = el.value; });
      writeDraft(scope, data);
      draft = data;
      if(flash !== false) showSaveBar("Saved ✓ " + savedTime(data.savedAt) + " — kept on this device");
    }
    form.addEventListener("input", function(){
      if(t) clearTimeout(t);
      t = setTimeout(function(){ save(true); }, 350);
    });
    form.addEventListener("change", function(){ save(true); });
    window.addEventListener("pagehide", function(){ if(t){ clearTimeout(t); save(false); } });
  });

  /* ---- Multi-job cart (pretend): kept on this device, in your bucket.
     (Was sessionStorage — it died when the browser closed. Now it lasts
     until the request is sent, like the drafts above.) ---- */
  function cartKey(){ return "bb_cart_v1:" + bbBucket(); }
  function getCart(){
    try{
      var raw = localStorage.getItem(cartKey());
      if(raw === null){
        var legacy = sessionStorage.getItem("bb_cart"); /* adopt a cart from before this change */
        if(legacy){ localStorage.setItem(cartKey(), legacy); sessionStorage.removeItem("bb_cart"); raw = legacy; }
      }
      return JSON.parse(raw || "[]");
    }catch(e){ return []; }
  }
  function setCart(c){ try{ localStorage.setItem(cartKey(), JSON.stringify(c)); }catch(e){} }

  var addBtn = document.getElementById("addJob");
  if(addBtn){
    addBtn.addEventListener("click", function(){
      var parts = [P.get("v"), P.get("p"), P.get("f")].filter(Boolean);
      var c = getCart();
      c.push({ j: P.get("j") || "Your job", size: parts.join(" — "), t: P.get("t") || "" });
      setCart(c);
      var t = P.get("t");
      location.href = "category.html" + (t ? "?t=" + encodeURIComponent(t) : "");
    });
  }
  var cartBtn = document.getElementById("cartBtn");
  if(cartBtn && getCart().length > 0){
    var n = getCart().length;
    cartBtn.textContent = "Your jobs (" + n + ") — review & send together";
    cartBtn.style.display = "block";
    var cnote = document.getElementById("cartNote");
    if(cnote){
      cnote.textContent = "You have " + n + " saved job" + (n > 1 ? "s" : "") +
        ". Add this one too, then send them all together from Your jobs — or just send this one on its own with the gold button.";
      cnote.style.display = "block";
    }
  }
  var cartList = document.getElementById("cartList");
  if(cartList){
    var renderCart = function(){
      var c = getCart();
      cartList.innerHTML = "";
      if(!c.length){
        cartList.innerHTML = '<p class="note">No jobs saved yet. Start a request, and on the review screen tap “Add another job” to build a list here.</p>';
        return;
      }
      c.forEach(function(job, i){
        var row = document.createElement("div");
        row.className = "kv";
        var txt = document.createElement("span");
        txt.textContent = job.j + (job.size ? " — " + job.size : "") + (job.t ? " · " + job.t : "");
        var rm = document.createElement("button");
        rm.type = "button"; rm.className = "rmbtn"; rm.textContent = "Remove";
        rm.addEventListener("click", function(){
          var cc = getCart(); cc.splice(i, 1); setCart(cc); renderCart();
        });
        row.appendChild(txt); row.appendChild(rm);
        cartList.appendChild(row);
      });
    };
    renderCart();
  }
  /* The request was sent — the cart and the in-progress request drafts
     have done their job, so they clear (a sent request never resurrects). */
  if(document.getElementById("clearCart")){
    setCart([]);
    clearDraft("request-details");
    clearDraft("request-other");
  }

  /* Cubic-yard helper (mulch). */
  var ydBtn = document.getElementById("ydBtn");
  if(ydBtn){
    ydBtn.addEventListener("click", function(){
      var v = parseFloat(document.getElementById("ydIn").value);
      var out = document.getElementById("ydOut");
      if(isNaN(v) || v <= 0){
        out.textContent = "Type the number of cubic yards.";
        return;
      }
      var tier = MULCH[mulchTier(v)];
      out.innerHTML = v + " cubic yards &rarr; that&rsquo;s the <span class='tier'>" +
        tier + "</span> size.";
      setUse(document.getElementById("ydUse"), tier + " (" + v + " cubic yards)");
    });
  }
})();
