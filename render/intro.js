// Five-second visual key; examples illustrate encodings, never additional data.
(function () {
  const C = KW_SYS.color, N = KW_SYS.nation;
  window.renderIntro = function (ctx, frame, width, height) {
    ctx.save(); ctx.scale(width / 1920, height / 1080);
    ctx.fillStyle = C.canvas; ctx.fillRect(0, 0, 1920, 1080);
    const t = frame / 30, font = 'ui-monospace, Menlo, Consolas, monospace';
    ctx.fillStyle = C.fg; ctx.font = '42px ' + font;
    ctx.fillText('How to read this world', 160, 112);
    ctx.fillStyle = C.fg2; ctx.font = '23px ' + font;
    ctx.fillText('Projects become land. Work brings it to life.', 160, 159);
    const rows = [
      ['Land', 'Clusters are projects; tiles are folders.'],
      ['Color / glow', 'Color = collaborator; brighter = more recent work.'],
      ['Flashes', 'Bigger burst = more output.'],
      ['Moving lines', 'Work to projects; local calls to machines.'],
      ['Pale lines', 'Project links / worktrees; fade on days 5–7.'],
      ['Circle + dot', 'Busiest agent-chat machine (inferred).'],
      ['Score / totals', 'Time below; recorded totals at right.']
    ];
    function hex(x, y, r, color) {
      ctx.fillStyle = color; ctx.beginPath();
      for (let i = 0; i < 6; i++) { const a = Math.PI / 3 * i + Math.PI / 6; const px = x + r * Math.cos(a), py = y + r * Math.sin(a); if (!i) ctx.moveTo(px, py); else ctx.lineTo(px, py); }
      ctx.closePath(); ctx.fill();
    }
    rows.forEach(([label, meaning], i) => {
      const y = 260 + i * 101;
      ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(160, y + 48); ctx.lineTo(1760, y + 48); ctx.stroke();
      ctx.fillStyle = C.fg; ctx.font = '26px ' + font; ctx.fillText(label, 350, y + 8);
      ctx.fillStyle = C.fg2; ctx.font = '25px ' + font; ctx.fillText(meaning, 660, y + 8);
      if (i === 0) { for (const [x, dy] of [[205,0],[239,-18],[239,18],[273,0]]) hex(x,y+dy,19,C.land); }
      if (i === 1) { [N.human,N.claude,N.codex,N.local_model].forEach((c,j)=>{ctx.globalAlpha=0.28+0.72*((t+j*0.45)%1.8)/1.8;hex(193+j*34,y,17,c);});ctx.globalAlpha=1; }
      if (i === 2) { [N.claude,N.codex].forEach((c,j)=>{const a=(t+j*0.7)%1.5, r=(j?24:14)+a*6;const g=ctx.createRadialGradient(218+j*56,y,0,218+j*56,y,r);g.addColorStop(0,c);g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.fillRect(218+j*56-r,y-r,r*2,r*2);ctx.beginPath();ctx.arc(218+j*56,y,r*(0.3+0.4*a/1.5),0,Math.PI*2);ctx.strokeStyle=C.canvas;ctx.lineWidth=4;ctx.stroke();ctx.strokeStyle=C.fg;ctx.lineWidth=1.4;ctx.stroke();ctx.fillStyle=C.fg;ctx.beginPath();ctx.arc(218+j*56,y,2,0,Math.PI*2);ctx.fill();}); }
      if (i === 3) { ctx.strokeStyle=N.local_model;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(184,y+14);ctx.quadraticCurveTo(237,y-38,298,y+14);ctx.stroke();const u=(t%1.3)/1.3;ctx.fillStyle=C.fg;ctx.beginPath();ctx.arc(184+114*u,y+14-104*u*(1-u),4,0,Math.PI*2);ctx.fill(); }
      if (i === 4) { ctx.strokeStyle=C.fg2;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(184,y+8);ctx.lineTo(264,y+8);ctx.moveTo(264,y+8);ctx.lineTo(294,y-16);ctx.moveTo(264,y+8);ctx.lineTo(303,y+25);ctx.stroke(); }
      if (i === 5) { const x=236+28*Math.sin(t*2);ctx.strokeStyle='rgba(240,232,205,0.85)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,14,0,Math.PI*2);ctx.stroke();ctx.fillStyle='rgba(240,232,205,0.9)';ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);ctx.fill(); }
      if (i === 6) { [N.human,N.claude,N.codex].forEach((c,j)=>{ctx.fillStyle=c;for(let k=0;k<4;k++){ctx.beginPath();ctx.arc(190+k*25,y-14+j*15,3+k%2,0,Math.PI*2);ctx.fill();}}); }
    });
    ctx.fillStyle=C.muted;ctx.font='19px '+font;ctx.fillText('Listen with headphones',160,1020);
    ctx.restore();
  };
})();
