// GSAP blob floats + card tilt (safe if GSAP not loaded)
(function(){
  const b1 = document.querySelector(".blob.b1");
  const b2 = document.querySelector(".blob.b2");
  const b3 = document.querySelector(".blob.b3");
  if (window.gsap && b1 && b2 && b3){
    gsap.to(b1,{x:40,y:20,scale:1.05,duration:8,yoyo:true,repeat:-1,ease:"sine.inOut"});
    gsap.to(b2,{x:-30,y:-10,scale:1.08,duration:10,yoyo:true,repeat:-1,ease:"sine.inOut"});
    gsap.to(b3,{x:10,y:-20,scale:1.02,duration:12,yoyo:true,repeat:-1,ease:"sine.inOut"});
  }

  const card = document.getElementById("loginCard");
  if (!card) return;
  let rect = null;
  const maxTilt = 10;
  const update = (e) => {
    rect = rect || card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    const rx = (maxTilt/2 - y * maxTilt);
    const ry = (x * maxTilt - maxTilt/2);
    card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateZ(0)`;
    card.style.setProperty("--mx", `${x*100}%`);
    card.style.setProperty("--my", `${y*100}%`);
  };
  const reset = () => { card.style.transform = ""; rect = null; };
  card.addEventListener("mousemove", update);
  card.addEventListener("mouseleave", reset);
  card.addEventListener("touchend", reset, {passive:true});
})();
