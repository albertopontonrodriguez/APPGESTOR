(() => {
  const intro=document.getElementById('intro');
  const counter=document.getElementById('countdown');
  const title=document.getElementById('introTitle');
  const icons=document.getElementById('introIcons');
  const canvas=document.getElementById('fireworks');
  const ctx=canvas.getContext('2d');
  let particles=[],raf,fireworkTimer;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

  function resize(){canvas.width=innerWidth*devicePixelRatio;canvas.height=innerHeight*devicePixelRatio;ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0)}
  addEventListener('resize',resize,{passive:true});resize();
  const colors=['#ffe66d','#ff5d8f','#43d9ff','#7cff8c','#ff963b','#ffffff','#b98cff'];
  function burst(x=Math.random()*innerWidth,y=innerHeight*(.18+Math.random()*.48)){
    const n=45+Math.floor(Math.random()*35),color=colors[Math.floor(Math.random()*colors.length)];
    for(let i=0;i<n;i++){
      const a=Math.PI*2*i/n+Math.random()*.15,s=2.2+Math.random()*5.5;
      particles.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:55+Math.random()*32,max:87,size:1.5+Math.random()*2.5,color,gravity:.055+Math.random()*.035});
    }
  }
  function draw(){
    ctx.clearRect(0,0,innerWidth,innerHeight);
    particles=particles.filter(p=>p.life>0);
    for(const p of particles){p.x+=p.vx;p.y+=p.vy;p.vy+=p.gravity;p.vx*=.992;p.life--;ctx.globalAlpha=Math.max(0,p.life/p.max);ctx.fillStyle=p.color;ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill()}
    ctx.globalAlpha=1;raf=requestAnimationFrame(draw);
  }
  draw();
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  async function run(){
    if(reduced){await wait(300);title.classList.add('show');counter.hidden=true;await wait(550);finish();return}
    for(const n of [3,2,1]){counter.textContent=n;counter.style.animation='none';void counter.offsetWidth;counter.style.animation='countPop .72s cubic-bezier(.2,.9,.2,1)';await wait(780)}
    counter.hidden=true;title.classList.add('show');icons.classList.add('show');
    burst(innerWidth*.22,innerHeight*.32);burst(innerWidth*.78,innerHeight*.27);burst(innerWidth*.50,innerHeight*.48);
    fireworkTimer=setInterval(()=>burst(),260);
    await wait(2100);finish();
  }
  function finish(){clearInterval(fireworkTimer);intro.classList.add('done');document.body.classList.remove('intro-active');setTimeout(()=>{cancelAnimationFrame(raf);intro.remove()},900)}
  run();
})();

const q=s=>document.querySelector(s),qa=s=>[...document.querySelectorAll(s)],vals=s=>qa(s).filter(x=>x.checked).map(x=>x.value);
const f=q('#f'),nd=q('#nd'),err=q('#err'),sum=q('#sum'),status=q('#status');
qa('input[name=n]').forEach(x=>x.onchange=()=>{nd.hidden=x.value==='0 noches';if(nd.hidden)qa('#nd input').forEach(i=>i.checked=false)});
function build(){
  const name=q('#name').value.trim(),days=vals('#fri,#sat'),n=q('input[name=n]:checked')?.value||'',sleep=vals('#sf,#ss'),bbq=vals('#bbq input'),med=q('input[name=med]:checked')?.value||'',tops=vals('#tops input'),sauces=vals('#sauces input'),e=[];
  if(!name)e.push('Escribe tu nombre.');if(!days.length)e.push('Selecciona al menos un día.');if(!n)e.push('Indica cuántas noches duermes.');if(n==='1 noche'&&sleep.length!==1)e.push('Selecciona exactamente una noche.');if(n==='2 noches'&&sleep.length!==2)e.push('Selecciona las dos noches.');if(days.includes('Viernes')&&!med)e.push('Indica si quieres 1 o 2 medallones.');if(!q('#ok').checked)e.push('Debes aceptar las condiciones de asistencia.');if(e.length)return{e};
  const add=(a,id)=>{const v=q(id).value.trim();if(v)a.push(v);return a};add(bbq,'#ob');add(tops,'#oh');add(sauces,'#os');
  const text=['🌴 *CONFIRMACIÓN · FINDE PARCELA*','',`👤 *Nombre:* ${name}`,`📅 *Días que voy:* ${days.join(', ')}`,`🛏️ *Me quedo:* ${n}`,sleep.length?`🌙 *Noche/s:* ${sleep.join(' y ')}`:'',`🔥 *Barbacoa:* ${bbq.length?bbq.join(', '):'Me adapto a todo'}`,days.includes('Viernes')?`🍔 *Hamburguesa:* ${med}`:'',days.includes('Viernes')?`🥒 *Ingredientes:* ${tops.length?tops.join(', '):'Solo carne'}`:'',days.includes('Viernes')?`🥫 *Salsas:* ${sauces.length?sauces.join(', '):'Sin salsa'}`:'',`⚠️ *Alergias:* ${q('#all').value.trim()||'Ninguna'}`,q('#notes').value.trim()?`💬 *Comentario:* ${q('#notes').value.trim()}`:'','','✅ Condiciones de asistencia aceptadas.'].filter(Boolean).join('\n');
  return{text};
}
function show(r){if(r.e){err.textContent=r.e.join(' ');err.style.display='block';sum.style.display='none';return}err.style.display='none';sum.textContent=r.text.replaceAll('*','');sum.style.display='block';return r.text}
f.onsubmit=e=>{e.preventDefault();const t=show(build());if(t)location.href='https://wa.me/?text='+encodeURIComponent(t)};
q('#copy').onclick=async()=>{const t=show(build());if(!t)return;try{await navigator.clipboard.writeText(t)}catch{const a=document.createElement('textarea');a.value=t;document.body.append(a);a.select();document.execCommand('copy');a.remove()}status.textContent='Confirmación copiada. Pégala en WhatsApp.'};
f.oninput=()=>status.textContent=q('#name').value.trim()&&vals('#fri,#sat').length?'Ya casi está. Revisa todo y pulsa enviar.':'Completa tu nombre y los días que vas.';
