/* =========================
  Rezoom — Global JS (fail-safe)
  ========================= */

// Mark page ready so CSS can apply enter states (keeps pages visible if scripts fail)
(function(){
  const ready = () => { try{ document.body.classList.add("js-ready"); }catch(e){} };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready);
  else ready();
})();

// Lenis smooth scrolling (optional)
(function(){
  try{
    // eslint-disable-next-line no-undef
    const lenis = new Lenis({ smoothWheel: true, syncTouch: true });
    function raf(t){ lenis.raf(t); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
  }catch(e){ /* no-op if Lenis not available */ }
})();

// Reveal-on-scroll with fallback
(function(){
  try{
    const els = document.querySelectorAll("[data-enter]");
    if (!els.length) return;
    if(!('IntersectionObserver' in window)){
      els.forEach(el=>el.classList.add('in-view'));
      return;
    }
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          entry.target.classList.add("in-view");
          io.unobserve(entry.target);
        }
      });
    }, {threshold:.15});
    els.forEach(el=> io.observe(el));
  }catch(e){
    document.querySelectorAll("[data-enter]").forEach(el=>el.classList.add("in-view"));
  }
})();

// GSAP sprinkles (optional)
(function(){
  if (!window.gsap) return;
  // eslint-disable-next-line no-undef
  gsap.registerPlugin(ScrollTrigger);
  gsap.utils.toArray("[data-pop]").forEach(el=>{
    // eslint-disable-next-line no-undef
    gsap.from(el,{
      opacity:0, y:14, duration:.7, ease:"power3.out",
      // eslint-disable-next-line no-undef
      scrollTrigger:{trigger:el, start:"top 88%"}
    });
  });
})();

// ✨ NEW: Interactive Login Card Glow ✨
(function(){
    const card = document.getElementById('login-card');
    if (!card) return;

    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const mx = (x / rect.width) * 100;
        const my = (y / rect.height) * 100;
        card.style.setProperty('--mx', `${mx}%`);
        card.style.setProperty('--my', `${my}%`);
    });

    card.addEventListener('mouseleave', () => {
        card.style.setProperty('--mx', `50%`);
        card.style.setProperty('--my', `50%`);
    });
})();