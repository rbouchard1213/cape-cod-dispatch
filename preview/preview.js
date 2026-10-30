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

  /* ---- Multi-job cart (pretend): jobs saved on this device only ---- */
  function getCart(){ try{ return JSON.parse(sessionStorage.getItem("bb_cart") || "[]"); }catch(e){ return []; } }
  function setCart(c){ try{ sessionStorage.setItem("bb_cart", JSON.stringify(c)); }catch(e){} }

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
  if(document.getElementById("clearCart")){ setCart([]); }

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
