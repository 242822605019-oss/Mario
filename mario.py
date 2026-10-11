import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Endless Platformer", page_icon="🍄", layout="wide")

st.title("🍄 Endless Platformer")
st.caption("A browser-based, Mario-inspired platform game built with Python + Streamlit. Original placeholder art; endless terrain is generated as you run.")

st.markdown("""
**How to play**
- **Desktop:** Arrow keys or **A/D** to move, **Space / W / ↑** to jump.
- **Mobile:** Use the on-screen ◀ ▶ and JUMP buttons.
- Collect coins, avoid enemies and gaps, and see how far you can go.
- Press **Restart** in the game to start a fresh run.
""")

game_html = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
  html,body { margin:0; padding:0; background:#111827; font-family:system-ui, sans-serif; overflow:hidden; }
  #wrap { width:100%; max-width:1100px; margin:0 auto; position:relative; }
  canvas { display:block; width:100%; height:auto; background:#87ceeb; border-radius:12px; touch-action:none; }
  #hud { position:absolute; left:12px; top:10px; display:flex; gap:8px; flex-wrap:wrap; z-index:2; }
  .pill { background:rgba(15,23,42,.84); color:white; border:1px solid rgba(255,255,255,.25); padding:6px 10px; border-radius:999px; font-weight:700; font-size:13px; }
  #restart { position:absolute; right:12px; top:10px; z-index:3; border:0; border-radius:999px; padding:8px 12px; font-weight:800; background:#fbbf24; color:#111827; cursor:pointer; }
  #mobile { display:none; position:absolute; bottom:14px; left:0; right:0; justify-content:space-between; padding:0 14px; z-index:3; pointer-events:none; }
  .cluster { display:flex; gap:10px; }
  .ctrl { pointer-events:auto; border:2px solid rgba(255,255,255,.6); background:rgba(15,23,42,.72); color:#fff; border-radius:16px; min-width:58px; height:58px; font-size:22px; font-weight:900; touch-action:none; user-select:none; }
  #jump { min-width:88px; font-size:15px; background:rgba(22,163,74,.88); }
  @media (max-width:700px) { #mobile { display:flex; } .pill {font-size:11px;padding:5px 8px;} }
</style>
</head>
<body>
<div id="wrap">
  <canvas id="game" width="960" height="540" aria-label="Endless platformer game"></canvas>
  <div id="hud">
    <div class="pill">🪙 Coins: <span id="coins">0</span></div>
    <div class="pill">🏁 Distance: <span id="distance">0</span> m</div>
    <div class="pill">⭐ Level: <span id="level">1</span></div>
  </div>
  <button id="restart">↻ Restart</button>
  <div id="mobile">
    <div class="cluster">
      <button class="ctrl" id="left">◀</button>
      <button class="ctrl" id="right">▶</button>
    </div>
    <button class="ctrl" id="jump">JUMP ⤴</button>
  </div>
</div>
<script>
(() => {
const canvas = document.getElementById('game'), ctx = canvas.getContext('2d');
const W=canvas.width, H=canvas.height;
const hudCoins=document.getElementById('coins'), hudDistance=document.getElementById('distance'), hudLevel=document.getElementById('level');
const keys = {left:false,right:false,jump:false};
let player, camera, platforms, coins, enemies, generatedUntil, scoreCoins, maxX, gameOver, lastTime, worldSpeed, particles;
const gravity=1900;
function rand(seed){ let x=Math.sin(seed*127.1+311.7)*43758.5453; return x-Math.floor(x); }
function reset(){
 player={x:100,y:300,w:30,h:42,vx:0,vy:0,onGround:false,alive:true,invuln:0};
 camera=0; platforms=[]; coins=[]; enemies=[]; particles=[];
 generatedUntil=0; scoreCoins=0; maxX=0; gameOver=false; worldSpeed=270; lastTime=0;
 platforms.push({x:0,y:455,w:760,h:100});
 generatedUntil=760; generateUntil(2600);
 updateHud();
}
function generateUntil(target){
 while(generatedUntil<target){
   let seed=Math.floor(generatedUntil/100)+13;
   let gap=rand(seed)*90+45;
   let width=rand(seed+1)*150+170;
   let x=generatedUntil+gap;
   let y=rand(seed+2)*115+335;
   // Keep jumps reasonable; avoid sudden huge height changes.
   if(platforms.length){ const py=platforms[platforms.length-1].y; y=Math.max(330,Math.min(430,py+(rand(seed+3)-.5)*100));}
   platforms.push({x,y,w:width,h:100});
   // Coin arcs over platforms
   let count=3+Math.floor(rand(seed+4)*4);
   for(let i=0;i<count;i++) coins.push({x:x+35+i*27,y:y-55-Math.sin(i/(count-1||1)*Math.PI)*24,r:9,taken:false});
   if(rand(seed+5)>.35 && x>600) enemies.push({x:x+width*(.45+rand(seed+6)*.25),y:y-30,w:28,h:30,dir:1,range:40+rand(seed+7)*45,origin:0});
   generatedUntil=x+width;
 }
}
function updateHud(){
 hudCoins.textContent=scoreCoins;
 hudDistance.textContent=Math.floor(maxX/10);
 hudLevel.textContent=Math.floor(maxX/1800)+1;
}
function hit(a,b){return a.x < b.x+b.w && a.x+a.w > b.x && a.y < b.y+b.h && a.y+a.h > b.y;}
function jump(){ if(player.onGround&&!gameOver){player.vy=-690;player.onGround=false;} else if(gameOver) reset(); }
function keyDown(e){
 if(['ArrowLeft','ArrowRight','ArrowUp',' ','Spacebar'].includes(e.key)) e.preventDefault();
 if(e.key==='ArrowLeft'||e.key.toLowerCase()==='a') keys.left=true;
 if(e.key==='ArrowRight'||e.key.toLowerCase()==='d') keys.right=true;
 if(e.key==='ArrowUp'||e.key===' '||e.key.toLowerCase()==='w'){ if(!e.repeat) jump(); keys.jump=true; }
 if(e.key.toLowerCase()==='r') reset();
}
function keyUp(e){
 if(e.key==='ArrowLeft'||e.key.toLowerCase()==='a') keys.left=false;
 if(e.key==='ArrowRight'||e.key.toLowerCase()==='d') keys.right=false;
 if(e.key==='ArrowUp'||e.key===' '||e.key.toLowerCase()==='w') keys.jump=false;
}
window.addEventListener('keydown',keyDown); window.addEventListener('keyup',keyUp);
function bindHold(id, key){
 const el=document.getElementById(id);
 const down=e=>{e.preventDefault();keys[key]=true;};
 const up=e=>{e.preventDefault();keys[key]=false;};
 el.addEventListener('pointerdown',down); el.addEventListener('pointerup',up); el.addEventListener('pointercancel',up); el.addEventListener('pointerleave',up);
}
bindHold('left','left'); bindHold('right','right');
document.getElementById('jump').addEventListener('pointerdown',e=>{e.preventDefault();jump();});
document.getElementById('restart').addEventListener('click',reset);
function update(dt){
 if(gameOver) return;
 worldSpeed=270+Math.min(180,maxX/65);
 let dir=(keys.right?1:0)-(keys.left?1:0);
 player.vx=dir*worldSpeed;
 if(!dir) player.vx*=.35;
 player.x+=player.vx*dt;
 if(player.x<camera+12) player.x=camera+12;
 player.vy+=gravity*dt; player.y+=player.vy*dt;
 player.onGround=false;
 for(const p of platforms){
   if(player.vy>=0 && player.x+player.w>p.x && player.x<p.x+p.w &&
      player.y+player.h>=p.y && player.y+player.h-player.vy*dt<=p.y+8){
       player.y=p.y-player.h; player.vy=0; player.onGround=true;
   }
 }
 for(const c of coins){
   if(!c.taken && hit(player,{x:c.x-c.r,y:c.y-c.r,w:c.r*2,h:c.r*2})){
     c.taken=true; scoreCoins++; particles.push({x:c.x,y:c.y,life:.45});
   }
 }
 for(const e of enemies){
   e.x+=e.dir*70*dt;
   if(!e.origin)e.origin=e.x;
   if(Math.abs(e.x-e.origin)>e.range)e.dir*=-1;
   if(hit(player,e)){
     if(player.vy>100 && player.y+player.h-e.y<22){ e.dead=true; player.vy=-420; scoreCoins+=2; }
     else { gameOver=true; }
   }
 }
 enemies=enemies.filter(e=>!e.dead && e.x>camera-200);
 if(player.y>H+100) gameOver=true;
 maxX=Math.max(maxX,player.x);
 camera=Math.max(0,player.x-260);
 generateUntil(camera+W+1100);
 particles=particles.filter(p=>{p.life-=dt;return p.life>0;});
 updateHud();
}
function rounded(x,y,w,h,r,color){
 ctx.fillStyle=color;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();
}
function draw(){
 ctx.clearRect(0,0,W,H);
 // Sky gradient
 let g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#73d7ff');g.addColorStop(1,'#e2f8ff');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 // distant clouds
 for(let i=0;i<8;i++){
   let x=((i*190-camera*.18)%(W+180)+W+180)%(W+180)-70, y=55+(i%3)*45;
   ctx.fillStyle='rgba(255,255,255,.78)';
   ctx.beginPath();ctx.ellipse(x,y,35,15,0,0,Math.PI*2);ctx.ellipse(x+24,y-8,25,18,0,0,Math.PI*2);ctx.ellipse(x+46,y,31,13,0,0,Math.PI*2);ctx.fill();
 }
 // rolling hills
 for(let i=0;i<7;i++){
   let x=((i*210-camera*.32)%(W+250)+W+250)%(W+250)-100;
   ctx.fillStyle=i%2?'#8bd67c':'#70c96a';ctx.beginPath();ctx.ellipse(x,H-35,150,95,0,Math.PI,Math.PI*2);ctx.fill();
 }
 // Platforms / ground
 for(const p of platforms){
   let x=p.x-camera;if(x+p.w<-30||x>W+30)continue;
   ctx.fillStyle='#9b633b';ctx.fillRect(x,p.y,p.w,p.h);
   ctx.fillStyle='#36b84d';ctx.fillRect(x,p.y,p.w,12);
   ctx.fillStyle='#72df63';for(let xx=x+8;xx<x+p.w;xx+=30)ctx.fillRect(xx,p.y+3,14,4);
   ctx.fillStyle='rgba(76,42,24,.35)';for(let xx=x+15;xx<x+p.w;xx+=48)ctx.fillRect(xx,p.y+28,18,5);
 }
 // Coins
 for(const c of coins){if(c.taken)continue;let x=c.x-camera;if(x<-20||x>W+20)continue;
   ctx.fillStyle='#f59e0b';ctx.beginPath();ctx.arc(x,c.y,c.r,0,Math.PI*2);ctx.fill();
   ctx.strokeStyle='#fff0a3';ctx.lineWidth=3;ctx.stroke();
   ctx.fillStyle='#fff4bd';ctx.fillRect(x-2,c.y-5,4,10);
 }
 // Enemies
 for(const e of enemies){let x=e.x-camera;if(x<-40||x>W+40)continue;
   rounded(x,e.y,e.w,e.h,8,'#a855f7');rounded(x+4,e.y+7,7,8,3,'#fff');rounded(x+17,e.y+7,7,8,3,'#fff');
   ctx.fillStyle='#1f2937';ctx.fillRect(x+7,e.y+10,3,4);ctx.fillRect(x+20,e.y+10,3,4);
   ctx.strokeStyle='#581c87';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x+5,e.y+e.h-2);ctx.lineTo(x+1,e.y+e.h+3);ctx.moveTo(x+23,e.y+e.h-2);ctx.lineTo(x+27,e.y+e.h+3);ctx.stroke();
 }
 // Player character, original simple adventurer
 let px=player.x-camera, py=player.y;
 // shadow
 ctx.fillStyle='rgba(15,23,42,.18)';ctx.beginPath();ctx.ellipse(px+15,py+43,18,5,0,0,Math.PI*2);ctx.fill();
 // legs/body
 rounded(px+5,py+23,9,17,3,'#2563eb');rounded(px+17,py+23,9,17,3,'#1d4ed8');
 rounded(px+4,py+12,23,18,5,'#ef4444');
 // face
 rounded(px+7,py+2,20,19,6,'#f7c98b');
 // cap
 rounded(px+4,py,24,8,4,'#dc2626');rounded(px+1,py+5,29,5,3,'#b91c1c');
 ctx.fillStyle='#111827';ctx.fillRect(px+20,py+10,3,5);
 // arms
 rounded(px,py+15,7,13,3,'#f7c98b');rounded(px+25,py+15,7,13,3,'#f7c98b');
 rounded(px+2,py+37,12,6,2,'#78350f');rounded(px+17,py+37,12,6,2,'#78350f');
 // particles
 for(const p of particles){ctx.globalAlpha=Math.max(0,p.life/.45);ctx.fillStyle='#fbbf24';ctx.font='bold 18px system-ui';ctx.fillText('+1',p.x-camera,p.y-p.life*45);ctx.globalAlpha=1;}
 if(gameOver){
   ctx.fillStyle='rgba(15,23,42,.72)';ctx.fillRect(0,0,W,H);
   ctx.textAlign='center';ctx.fillStyle='#fff';ctx.font='bold 46px system-ui';ctx.fillText('RUN OVER!',W/2,H/2-35);
   ctx.font='bold 22px system-ui';ctx.fillText('Distance: '+Math.floor(maxX/10)+' m   •   Coins: '+scoreCoins,W/2,H/2+8);
   ctx.font='18px system-ui';ctx.fillText('Press R, tap Restart, or jump to try again',W/2,H/2+48);ctx.textAlign='left';
 }
}
function loop(t){
 if(!lastTime)lastTime=t;let dt=Math.min((t-lastTime)/1000,.035);lastTime=t;
 update(dt);draw();requestAnimationFrame(loop);
}
reset();requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""

components.html(game_html, height=590, scrolling=False)

with st.expander("How it works"):
    st.markdown("""
    - **Python + Streamlit** serves the page and its instructions.
    - **HTML Canvas + JavaScript** runs the real-time game loop inside the browser; this is needed for smooth keyboard/touch controls and animation.
    - Terrain, coin groups, and enemies are generated procedurally as the camera advances, so there is no fixed final level.
    - This is a starter prototype. Scores currently last only for the current run/session; persistent leaderboards, sound, sprites, and APK packaging can be added later.
    """)

st.caption("Prototype game — not affiliated with or using Nintendo's Mario assets.")
