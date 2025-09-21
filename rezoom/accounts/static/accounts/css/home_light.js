// Minimal reveal-on-scroll just for the homepage
(function(){
  const els = document.querySelectorAll(".reveal");
  if (!els.length) return;
  if(!("IntersectionObserver" in window)){
    els.forEach(el=> el.classList.add("in"));
    return;
  }
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{
      if(e.isIntersecting){ e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, {threshold:.12});
  els.forEach(el=> io.observe(el));
})();
