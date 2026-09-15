from pathlib import Path

p=Path(__file__).parents[1]/'index.html';s=p.read_text();s=s.replace('<div id="results"></div></section><section class="box" id="guide">','<div id="match-results"></div></section><section class="box" id="guide">',1);s=s.replace('results.innerHTML=r.map','document.getElementById(\'match-results\').innerHTML=r.map',1);p.write_text(s)
