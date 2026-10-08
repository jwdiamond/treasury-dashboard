
const D = window.DASHBOARD_DATA;
const fmtPct = v => `${Number(v).toFixed(2)}%`;
const fmtBp = v => `${Math.round(v)} bp`;
const signBp = v => `${v >= 0 ? "+" : ""}${Math.round(v)} bp`;
const fmtT = v => `$${Number(v).toFixed(2)}T`;
const fmtB = v => `$${v >= 0 ? "+" : ""}${Number(v).toFixed(1)}B`;

document.getElementById("asof").textContent =
  `Market data through ${D.meta.market_date} · Treasury debt snapshot ${D.meta.mspd_date}`;
document.getElementById("ust10").textContent = fmtPct(D.market.ust10);
document.getElementById("real10").textContent = fmtPct(D.market.real10);
document.getElementById("ig").textContent = fmtBp(D.market.ig_oas);
document.getElementById("bbb").textContent = fmtBp(D.market.bbb_oas);
document.getElementById("hy").textContent = fmtBp(D.market.hy_oas);
document.getElementById("ust10chg").textContent = `${signBp(D.market.ust10_5d_bp)} over 5 observations`;
document.getElementById("bbbchg").textContent = `${signBp(D.market.bbb_5d_bp)} over 5 observations`;
document.getElementById("regime").textContent = D.market.regime;
document.getElementById("regimeExplain").textContent =
  (D.market.ust10_5d_bp > 0 && D.market.bbb_5d_bp > 0)
  ? "Treasury yields and BBB corporate spreads are rising together, increasing borrowing costs through both the risk-free rate and the credit-risk premium."
  : "Rates and credit spreads are not currently moving in the same tightening direction.";

document.getElementById("debtTotal").textContent = fmtT(D.debt.marketable_debt_trillions);
document.getElementById("wam").textContent = `${D.debt.wam_years.toFixed(2)} yrs`;
document.getElementById("duration").textContent = `${D.debt.modified_duration_years.toFixed(2)} yrs`;
document.getElementById("mspd").textContent = `MSPD snapshot: ${D.meta.mspd_date}`;

const plotCfg = {displayModeBar:false,responsive:true};
const baseLayout = {
  margin:{l:58,r:18,t:20,b:45},
  paper_bgcolor:"#ffffff", plot_bgcolor:"#ffffff",
  font:{family:"Inter, system-ui, sans-serif",color:"#42515e",size:12},
  xaxis:{gridcolor:"#eef2f5",zeroline:false},
  yaxis:{gridcolor:"#eef2f5",zeroline:false},
  legend:{orientation:"h",y:-0.22},
  hovermode:"x unified"
};

const H = D.credit_history || [];
if (H.length > 1) {
  Plotly.newPlot("creditChart",[
    {x:H.map(d=>d.date),y:H.map(d=>d.ig),name:"IG OAS",mode:"lines",line:{width:2}},
    {x:H.map(d=>d.date),y:H.map(d=>d.bbb),name:"BBB OAS",mode:"lines",line:{width:2}},
    {x:H.map(d=>d.date),y:H.map(d=>d.hy),name:"High Yield OAS",mode:"lines",line:{width:2}}
  ],{...baseLayout,yaxis:{...baseLayout.yaxis,title:"Basis points"}},plotCfg);
  Plotly.newPlot("tighteningChart",[
    {x:H.map(d=>d.date),y:H.map(d=>d.ust10_5d_bp),name:"10Y Treasury, 5-day change",mode:"lines",line:{width:2}},
    {x:H.map(d=>d.date),y:H.map(d=>d.bbb_5d_bp),name:"BBB OAS, 5-day change",mode:"lines",line:{width:2}}
  ],{...baseLayout,yaxis:{...baseLayout.yaxis,title:"Basis points"},shapes:[{type:"line",x0:0,x1:1,xref:"paper",y0:0,y1:0,line:{width:1,dash:"dot"}}]},plotCfg);
} else {
  document.getElementById("creditChart").innerHTML = "<div class='empty'>Historical chart will populate after you run the exporter against credit_market_history.csv.</div>";
  document.getElementById("tighteningChart").innerHTML = "<div class='empty'>Historical chart will populate after you run the exporter against credit_market_history.csv.</div>";
}

Plotly.newPlot("bucketChart",[{
  x:D.debt.maturity_buckets.map(d=>d.horizon),
  y:D.debt.maturity_buckets.map(d=>d.amount),
  type:"bar",
  hovertemplate:"%{x}: $%{y:.2f}T<extra></extra>"
}],{
  ...baseLayout,
  showlegend:false,
  xaxis:{
    ...baseLayout.xaxis,
    type:"category",
    title:"Maturity horizon"
  },
  yaxis:{
    ...baseLayout.yaxis,
    title:"$ trillions"
  }
},plotCfg);

Plotly.newPlot("compositionChart",[{
  labels:D.debt.composition.map(d=>d.security),
  values:D.debt.composition.map(d=>d.amount),
  type:"pie",hole:.52,textinfo:"label+percent",hovertemplate:"%{label}: $%{value:.2f}T<extra></extra>"
}],{...baseLayout,margin:{l:35,r:35,t:25,b:55},showlegend:false},plotCfg);

const R = D.refinancing;
Plotly.newPlot("refiDebtChart",[{
  x:R.map(d=>String(d.year)),y:R.map(d=>d.maturing),type:"bar",
  hovertemplate:"%{x}: $%{y:.2f}T<extra></extra>"
}],{...baseLayout,showlegend:false,yaxis:{...baseLayout.yaxis,title:"$ trillions"}},plotCfg);

Plotly.newPlot("interestChart",[{
  x:R.map(d=>String(d.year)),y:R.map(d=>d.interest_change),type:"bar",
  hovertemplate:"%{x}: $%{y:.1f}B<extra></extra>"
}],{...baseLayout,showlegend:false,yaxis:{...baseLayout.yaxis,title:"$ billions / year"}},plotCfg);

document.getElementById("refiTable").innerHTML = R.map(r => `
<tr>
  <td>${r.year}</td><td>${fmtT(r.maturing)}</td><td>${r.coupon.toFixed(2)}%</td>
  <td>${r.replacement.toFixed(2)}%</td><td>+${Math.round(r.reset_bp)} bp</td>
  <td>${fmtB(r.interest_change)}</td>
</tr>`).join("");
