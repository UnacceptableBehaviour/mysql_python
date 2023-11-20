//import { dtkChartData } from '/dtk_wgt_graph/static/js_modules/content/dtk_data_process.js';
import { dtkChartData } from '/static/dtk_data_process.js';

const CHART_WIDTH_DAYS_DEFAULT = 14;
const INDEX_END_DEFAULT = parseInt(dtkChartData.length);
const INDEX_START_DEFAULT = parseInt(INDEX_END_DEFAULT - CHART_WIDTH_DAYS_DEFAULT);

class DisplayObject {
  constructor({display, doName, x_pc, y_pc, w_pc, h_pc, x1_pc, y1_pc, radius_pc, arc_rad, col_ink, col_bk, alpha, fontSize=10, col_bbox='magenta', dbgOn=false} = {}){
		this.display = display;
    this.ctx = this.display.canvas.getContext("2d");
    this.doName = doName;
    this.x_pc = x_pc;
    this.x = this.display.canvas.width * (this.x_pc / 100);
    this.y_pc = y_pc;
    this.y = this.display.canvas.height * (this.y_pc / 100);
    this.w_pc = w_pc;
    this.w = this.display.canvas.width * (this.w_pc / 100);
    this.h_pc = h_pc;
    this.h = this.display.canvas.height * (this.h_pc / 100);
    this.x1_pc = x1_pc;
    this.x1 = this.display.canvas.width * (this.x1_pc / 100);
    this.y1_pc = y1_pc;
    this.y1 = this.display.canvas.height * (this.y1_pc / 100);
    this.radius_pc = radius_pc;
    this.arc_rad = arc_rad;
    this.col_ink = col_ink;
    this.col_bk = col_bk;
    this.alpha = alpha;
    this.col_bbox = col_bbox;
    this.fontSize = fontSize;

    // debug
    this.dbgOn = dbgOn;
    this.border = dbgOn;
    this.titleOn = dbgOn;
    this.markers = false; //dbgOn;
    this.textEdgeMarkers = dbgOn;
  }

  scaleCoords(){
    this.x = this.display.canvas.width * (this.x_pc / 100);
    this.y = this.display.canvas.height * (this.y_pc / 100);
    this.w = this.display.canvas.width * (this.w_pc / 100);
    this.h = this.display.canvas.height * (this.h_pc / 100);
    this.x1 = this.display.canvas.width * (this.x1_pc / 100);
    this.y1 = this.display.canvas.height * (this.y1_pc / 100);
  }


  draw(){
    this.scaleCoords();
    this.ctx.save();
    if (this.border) { // boundingBox
      //this.drawLineCentre2Obj();
      //console.log(`doName: ${this.doName}, x: ${this.x}, y: ${this.y}, w: ${this.w}, h: ${this.h}, ink:${this.col_ink}, bbox:${this.col_bbox}`); 

      // border - guideline for now
      this.ctx.beginPath();
      this.ctx.strokeStyle = this.col_bbox;      
      this.ctx.lineWidth = 1;
      this.ctx.rect(this.x, this.y, this.w, this.h);
      this.ctx.stroke();
    }
    if (this.titleOn) {      
      //placeCentreText(this.ctx, text, xl, xr, y, color, fontSize, lnW = 2)
      this.placeCentreText(this.ctx, this.doName, this.x, this.x + this.w, this.y + this.h, this.col_ink, this.fontSize);
      //console.log(`title: ${this.doName} :ON`);
    } else {      
      //console.log(`title: ${this.doName} :OFF`);
    }
    if (this.markers) {
      // show rect place
      //drawCircle(this.x, this.y, 6, 'cyan');
      this.ctx.beginPath();
      this.ctx.fillStyle = 'cyan';
      this.ctx.arc(this.x, this.y, 6, 0, 2*Math.PI);
      this.ctx.fill();
      
      // show translate place
      //drawCircle(this.x + this.w/2, this.y + this.h/2, 6, 'orange');
      this.ctx.beginPath();
      this.ctx.fillStyle = 'orange';
      this.ctx.arc(this.x + this.w/2, this.y + this.h/2, 6, 0, Math.PI*2);
      this.ctx.fill();

      // show origin
      //drawCircle(0, 0, 3, 'blue');
      this.ctx.translate(0, 0);     
      this.ctx.beginPath();
      this.ctx.fillStyle = 'blue';
      this.ctx.arc(0, 0, 3, 0, 2*Math.PI);
      this.ctx.fill();       
    }    
    this.ctx.restore();
  }

  placeText(ctx=null, text, x, y, color, fontSize, align='center', baseline='middle') {    
    if (ctx==null){ ctx = this.ctx };
    ctx.save();
    
    // font def
    ctx.font = `${fontSize}px Arial`;
    ctx.textBaseline = baseline; // hanging
    ctx.textAlign = align;  // 'left' 'center'
      
    let textMetrics = ctx.measureText(text);
    console.log('textMetrics');
    console.log(textMetrics);
  
    // place text between if it fits below if not
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
    ctx.restore();

    return textMetrics;
  }    

  // const baselines = ["top","hanging","middle","alphabetic","ideographic","bottom"];
  placeCentreTextNoMk(ctx=null, text, xl, xr, y, color, fontSize, align='center', baseline='middle') {    
    if (ctx==null){ ctx = this.ctx };
    //   |                                 |      < fontSize(epth)
    //   xl             texts              xr
    //                    |
    //                    ^ markMidddle
    ctx.save();
    
    // font def
    ctx.font = `${fontSize}px Arial`;
    ctx.textBaseline = baseline; // hanging
    ctx.textAlign = align;  // 'left' 'center'
      
    let markMiddle = xl + (xr - xl) / 2;
    let textMetrics = ctx.measureText(text);
    let textStart = markMiddle;   
  
    // place text between if it fits below if not
    ctx.fillStyle = color;
    ctx.fillText(text, textStart, y+fontSize);
    ctx.restore();
  }  

  placeCentreText(ctx=null, text, xl, xr, y, color, fontSize, lnW = 2) {    
    if (ctx==null){ ctx = this.ctx };
    //   |                                 |      < fontSize(epth)
    //   xl             texts              xr
    //                    |
    //                    ^ markMidddle
    ctx.save();
    
    // font def
    ctx.font = `${fontSize}px Arial`;
    ctx.textBaseline = 'middle'; // hanging
    ctx.textAlign = 'center';
      
    let markMiddle = xl + (xr - xl) / 2;
    let textMetrics = ctx.measureText(text);
    let textStart = markMiddle;
    
    if (this.textEdgeMarkers) {
      // place left vert line
      ctx.beginPath();
      ctx.lineWidth = lnW;
      ctx.strokeStyle = color;
      ctx.moveTo(xl, y);
      ctx.lineTo(xl, y+fontSize);  // line depth - marker depth
      ctx.stroke(); 
    
      // place right vert line
      ctx.beginPath();
      ctx.lineWidth = lnW;
      ctx.strokeStyle = color;
      ctx.moveTo(xr, y);
      ctx.lineTo(xr, y+fontSize);  // line depth - marker depth
      ctx.stroke();
    }
  
    // place text between if it fits below if not
    ctx.fillStyle = color;
    ctx.fillText(text, textStart, y+fontSize);
    ctx.restore();
  }  

  drawLineCentre2Obj(){
    let x_c = this.display.canvas.width / 2;
    let y_c = this.display.canvas.height / 2;
    this.ctx.beginPath();
    this.ctx.moveTo(x_c, y_c);
    this.ctx.lineTo(this.x, this.y);
    this.ctx.strokeStyle = this.col_ink;
    this.ctx.lineWidth = 4;
    this.ctx.stroke();
  }

  drawCircle(x,y,w,col,rad_start=0,rad_end=Math.PI * 2) {
    this.ctx.beginPath();
    this.ctx.arc(x, y, w, rad_start, rad_end);
    this.ctx.closePath();
    this.ctx.fillStyle = col;
    this.ctx.fill();
  }  
}

class VertLabelBar extends DisplayObject {
  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                label_top='#',label_bot='#', pwPos=1, periodWindow=7, dark=null  )
  {
    if (dark === null) dark = pwPos % 2;   // 0=dark 1=light
    if (dark > 0) dark = 1;
    
    alpha = alpha * dark;
    
    x_pc = (pwPos-1) * (100 / periodWindow);
    y_pc = 0;
    w_pc = (100 / periodWindow);
    h_pc = 100;
    super({ display:display, doName:doName, 
      x_pc:x_pc, y_pc:y_pc, w_pc:w_pc, h_pc:h_pc, arc_rad:arc_rad, 
      col_ink:col_ink, col_bk:col_bk, alpha:alpha, fontSize:fontSize, col_bbox:col_bbox, dbgOn:dbgOn});

    this.label_top    = label_top;
    this.label_bot    = label_bot;
    this.pwPos        = pwPos;
    this.periodWindow = periodWindow;    
    this.dark         = dark;
  }  

  draw(){
    super.draw();
    const ctx = this.display.canvas.getContext("2d");
    ctx.fillStyle = this.col_ink;
    ctx.globalAlpha = this.alpha;
    ctx.fillRect(this.x, this.y, this.w, this.h);
    ctx.globalAlpha = 1;                                        // TODO - sort propert geometry calculation out for text placement
    this.placeCentreTextNoMk(ctx, this.label_top, this.x, this.x + this.w, this.y + (this.h - (this.h/this.fontSize)-this.fontSize), this.col_ink, this.fontSize );
    this.placeCentreTextNoMk(ctx, this.label_bot, this.x, this.x + this.w, this.y + (this.h - (this.h/this.fontSize)+this.fontSize), this.col_ink, this.fontSize );
    //console.log(`VertLabelBar ${this.label} - dark:${this.dark} - alpha:${this.alpha}  \tx:${this.x_pc}, y:${this.y_pc}, w:${this.w_pc}, h:${this.h_pc},`);
  }
}

class VertLabelBars extends DisplayObject {
  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                dtkChart )
  {
    super({ display:display, doName:doName, 
      x_pc:x_pc, y_pc:y_pc, w_pc:w_pc, h_pc:h_pc, arc_rad:arc_rad, 
      col_ink:col_ink, col_bk:col_bk, alpha:alpha, fontSize:fontSize, col_bbox:col_bbox, dbgOn:dbgOn});
      this.fontSize = fontSize;
      this.dtkChart = dtkChart;
  }

  draw(){
    super.draw();
    let periodWindow  = this.dtkChart.chartSettings.chartWidthDays;
    let endIndex      = this.dtkChart.chartSettings.endIndex;
    let startIndex    = endIndex - periodWindow;

    for (let pwPos = 0; pwPos < periodWindow; pwPos++){
      let dsObjConfig = { display:this.display, doName:'vBar', 
      //x_pc:80, y_pc:0, w_pc:20, h_pc:100, arc_rad:0, 
      col_ink:'black', col_bk:'white', alpha:0.1, fontSize:this.fontSize, col_bbox:'cyan', dbgOn:false};
      
      let dataIdxOffset = startIndex+pwPos;
      let dayShort = dtkChartData[dataIdxOffset].dtk_rcp.dt_day.slice(0,2);;
      let dayNum = dtkChartData[dataIdxOffset].dtk_rcp.dt_date_readable.slice(-2); // last 2 chars
      let vBar = new VertLabelBar(dsObjConfig, dayShort, dayNum, pwPos+1, periodWindow );
      vBar.draw();
    }
  }
}


class YAxisNumbering extends DisplayObject {
  constructor({display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
              dtkChart)
  {
    super({ display, doName,
            x_pc, y_pc, w_pc, h_pc, arc_rad,
            col_ink, col_bk, alpha, fontSize,
            col_bbox, dbgOn
    });
    this.fontSize = fontSize + 4;
    this.dtkChart = dtkChart;
    this.getBoundaryValues();
  }

  getBoundaryValues() {
    if (this.dtkChart){
      const {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange} = this.dtkChart;
      Object.assign(this, {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange});
    }
  }

  getIntegersBetween(a, b) { // [103, 104, 105, 106, 107]
    let start = Math.ceil(a);
    let end = Math.floor(b);
    let result = [];
    for (let i = start; i <= end; i++) {
        result.push(i);
    }
    return result;
  }

  getIntegersBetweenReverse(a, b) { // [107, 106, 105, 104, 103]
    let start = Math.ceil(a);
    let end = Math.floor(b);
    let result = [];
    for (let i = end; i >= start; i--) {
        result.push(i);
    }
    return result;
  }  

  draw(){
    // this.yAxisMinVal = y = 100%
    // this.yAxisMaxVal = y = 0%
    // this.yAxisRange  = canvas 100%

    this.getBoundaryValues();

    let labels = this.getIntegersBetweenReverse(this.yAxisMinVal, this.yAxisMaxVal); // REF in func no PASS
    
    super.draw();
    let ctx = this.display.canvas.getContext("2d");
    //let cH = this.display.canvas.height;
    let cW = this.display.canvas.width;

    let noOfhMarks = labels.length;      
    let x2 = cW;

    for (let mkNo = 0; mkNo < noOfhMarks; mkNo++ ){
      let yLabelText = labels[mkNo]; //baselines[mkNo+2];
      //console.log(ctx.measureText(yLabelText));
      let x1 = ctx.measureText(yLabelText).width + this.fontSize;

      let yVal = parseFloat(yLabelText);
      let yPosFromRangeMin = yVal - this.yAxisMinVal; 

      let yPosFromMin_pc  = (yPosFromRangeMin / this.yAxisRange) * 100;
      // this.yAxisRange (range 104.0 to 108.0) range = 4.0
      this.y_pc  = 100 - yPosFromMin_pc;  
      this.scaleCoords(); // convert y_pc to y

      ctx.globalAlpha = this.alpha;
      ctx.beginPath();
      ctx.moveTo(x1, this.y);
      ctx.lineTo(x2, this.y);
      ctx.strokeStyle = this.col_ink;
      ctx.lineWidth = 1;      
      ctx.setLineDash([5, 15]); // dash gap - eg [5, 10, 15, 20]
      ctx.stroke();
      this.placeCentreTextNoMk(ctx, yLabelText, 0, x1, this.y - this.fontSize, this.col_ink, this.fontSize, 'center', 'middle');
      ctx.globalAlpha = 1;
      ctx.setLineDash([]);
    }
    
  }

}


class DataPoint extends DisplayObject {
  static NONE     = 0;
  static CIRCLE   = 1;
  static SQUARE   = 2;
  static DIAMOND  = 3;
  static CROSS    = 4;
  static CROSSX   = 5;

  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, radius_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                yVal, pointType=DataPoint.CIRCLE )
  {
    super({ display, doName,
      x_pc, y_pc, w_pc, h_pc, radius_pc, arc_rad,
      col_ink, col_bk, alpha, fontSize,
      col_bbox, dbgOn
    });    
    this.fontSize   = fontSize;
    this.pointType  = pointType;
    this.yVal       = yVal;
  }

  draw(){
    super.draw(); // scale x_pc,y_pc
    let ctx = this.display.canvas.getContext("2d");

    if (this.pointType == DataPoint.NONE) {      
    } else if (this.pointType == DataPoint.CIRCLE) {      
      this.drawCircle(this.x,this.y,this.radius_pc/2,this.col_ink);
    } else if (this.pointType == DataPoint.SQUARE) {
      this.drawCircle(this.x,this.y,this.w/2,this.col_ink);
    } else if (this.pointType == DataPoint.DIAMOND) {
      this.drawCircle(this.x,this.y,this.w/2,this.col_ink);
    } else if (this.pointType == DataPoint.CROSS) {
      this.drawCircle(this.x,this.y,this.w/2,this.col_ink);
    } else if (this.pointType == DataPoint.CROSSX) {
      this.drawCircle(this.x,this.y,this.w/2,this.col_ink);
    }

    let pointLabelText = `${this.yVal.toFixed(1)}`;

    let leftOfDataPoint = true;
    if (leftOfDataPoint) {
      let xr = this.x - this.radius_pc*4;  
      let xl = xr - ctx.measureText(pointLabelText).width;            
      this.placeCentreTextNoMk(ctx, pointLabelText, xl, xr, this.y - this.fontSize, this.col_ink, this.fontSize, 'center', 'middle');
    } else {
      let xl = this.x + this.radius_pc*4;
      let xr = xl + ctx.measureText(pointLabelText).width;  
      this.placeCentreTextNoMk(ctx, pointLabelText, xl, xr, this.y - this.fontSize, this.col_ink, this.fontSize, 'center', 'middle');
    }

    
    
  }
}

class ScaledLine extends DisplayObject {
  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, x1_pc, y1_pc, col_ink, col_bk, alpha, dbgOn} = {},
    lineDash=[], lineWidth=1 )
  {
    super({ display:display, doName:doName, 
            x_pc:x_pc, y_pc:y_pc, x1_pc:x1_pc, y1_pc:y1_pc,
            col_ink:col_ink, col_bk:col_bk, alpha:alpha, dbgOn:dbgOn});
    
    this.lineDash = lineDash;
    this.lineWidth = lineWidth;        
  }

  draw(){
    let ctx = this.display.canvas.getContext("2d");
    this.scaleCoords(); // convert y_pc to y

    ctx.globalAlpha = this.alpha;
    ctx.beginPath();
    ctx.moveTo(this.x, this.y);
    ctx.lineTo(this.x1, this.y1);
    ctx.strokeStyle = this.col_ink;
    ctx.lineWidth = this.lineWidth;      
    ctx.setLineDash(this.lineDash); // dash gap - eg [5, 10, 15, 20]
    ctx.stroke();    
    ctx.globalAlpha = 1;
    ctx.setLineDash([]);
  }
}

class DataPlot extends DisplayObject {
  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                dtkChart, dataSourceKey, label='#', pointType=DataPoint.CIRCLE  )
  {
    super({ display, doName,
      x_pc, y_pc, w_pc, h_pc, arc_rad,
      col_ink, col_bk, alpha, fontSize,
      col_bbox, dbgOn
    });

    //          / - - - dataSourceKey
    // {       /
    //   dtk_pc_fat: "38.3",
    //   dtk_pc_h2o: "44.8",
    //   dtk_rcp: {
    //     dt_date: 1568764800000,
    //     dt_date_readable: "2019 09 18",
    //     dt_day: "day",
    //   },
    //   dtk_user_info: { UUID: "x-x-x-x-xxx", name: "AGCT" },
    //   dtk_weight: "105.7",
    // }       
    this.dtkChart       = dtkChart;
    this.dataSourceKey  = dataSourceKey;
    this.label          = label;    
    this.pointType      = pointType;
    this.getBoundaryValues();    
    this.radius_pc      = this.xIncrement_pc / 6;

    console.log(`min: ${this.yAxisMinVal}, max: ${this.yAxisMaxVal}, range: ${this.yAxisRange} <`);
  }  

  getBoundaryValues() {
    if (this.dtkChart){
      const {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange} = this.dtkChart;
      Object.assign(this, {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange});
    }
  }
  
  // 
  draw(){
    this.getBoundaryValues();
    console.log(`xIncrement_pc: ${this.xIncrement_pc}, dataMin: ${this.dataMin}, dataMax: ${this.dataMax},\nyAxisRange: ${this.yAxisRange}, yAxisMinVal: ${this.yAxisMinVal}, yAxisMaxVal: ${this.yAxisMaxVal}`);
    
    super.draw();

    //console.log(`cH:${cH} scaling[${yScaling}] - lab:${labels[mkNo]}`);
    
    //console.log(`pwPos:${pwPos} > yVal: ${yVal}  x2: ${x2}, y1: ${y1} lab:${labels[mkNo]} , y1: ${y1}`);

    let x_pc = this.xIncrement_pc / 3;
    let prevX_pc = x_pc - this.xIncrement_pc;
    let prevY_pc = parseFloat(dtkChartData[this.startIndex-1][this.dataSourceKey]);
    for (let pwPos = this.startIndex; pwPos < this.endIndex; pwPos++){
      // place in range (range 104.0 to 108.0) 105.2 = 1.2
      let y_pc = this.dtkChart.yPcFromyVal(parseFloat(dtkChartData[pwPos][this.dataSourceKey]));

      let dsObjConfig = { display:this.display, doName:`${y_pc}`, 
          x_pc:prevX_pc,  y_pc:prevY_pc,
          x1_pc:x_pc,     y1_pc:y_pc,          
          col_ink:this.dtkChart.chartSettings.col_ink[this.dataSourceKey], col_bk:'white', alpha:1, fontSize:this.fontSize,
          col_bbox:'cyan', dbgOn:false };

      // let point = new DataPoint(dsObjConfig, yVal, this.pointType);
      // point.draw();
      let tl = new ScaledLine(dsObjConfig, [15,5], 2);
      tl.draw();
      prevX_pc = x_pc;
      prevY_pc = y_pc;
      x_pc += this.xIncrement_pc;
    }

    x_pc = this.xIncrement_pc / 3;
    for (let pwPos = this.startIndex; pwPos < this.endIndex; pwPos++){
      // place in range (range 104.0 to 108.0) 105.2 = 1.2
      let yVal = parseFloat(dtkChartData[pwPos][this.dataSourceKey]);
      let yPosFromRangeMin = yVal - this.yAxisMinVal; 

      let yPosFromMin_pc  = (yPosFromRangeMin / this.yAxisRange) * 100;
      // this.yAxisRange (range 104.0 to 108.0) range = 4.0
      let y_pc  = 100 - yPosFromMin_pc;   // 100 - y_pc to invert because 0,0 is at the top!

      let dsObjConfig = { display:this.display, doName:`${y_pc}`, 
          x_pc:x_pc, y_pc:y_pc, radius_pc:this.radius_pc, 
          col_ink:'black', col_bk:'white', alpha:1, fontSize:this.fontSize,
          col_bbox:'cyan', dbgOn:true};

      let point = new DataPoint(dsObjConfig, yVal, this.pointType);
      point.draw();
      x_pc += this.xIncrement_pc;
    }

    // let tl = new ScaledLine({ display:this.display, x_pc:10, y_pc:10, x1_pc:90, y1_pc:90, col_ink:'rgb(255, 111, 0)', alpha:1}, [5,5], 5);
    // tl.draw();

  }
}


class ChartKey extends DisplayObject {
  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                dtkChart, title='#' )
  {
    super({ display, doName,
      x_pc, y_pc, w_pc, h_pc, arc_rad,
      col_ink, col_bk, alpha, fontSize,
      col_bbox, dbgOn
    });

    this.dtkChart = dtkChart;
    this.title    = title;
    this.keyTxt   = [];
    this.keyCol   = [];
    this.keyCount = 0;
    this.longestText = title.length;    

    this.spacer = this.fontSize *1.5; 
    this.colRectSz = this.spacer * 0.7;
    this.vOffset = this.spacer * 0.3;

    this.w = (this.spacer * 2.5) + (this.longestText * 6);

    console.log(`ChartKey   : ${this.x},${this.y},${this.w},${this.h} <`);
    console.log(`ChartKey pc: ${this.x_pc},${this.y_pc},${this.w_pc},${this.h_pc} <`);
  }

  addKey(label, col){
    this.keyTxt[this.keyCount] = label;
    this.keyCol[this.keyCount] = col;
    this.keyCount++;
    
    if (label.length > this.longestText) this.longestText = label.length;

    this.h = this.vOffset + this.spacer + (this.spacer * this.keyCount);
    this.w = (this.spacer * 2.5) + (this.longestText * 6);
    
    console.log(`ChartKey[${this.keyCount}]ADD: ${label}(${label.length})(${this.longestText}),${col} w:${this.w},h:${this.h}<`);
  }

  clearKeys(){
    this.keyTxt   = [];
    this.keyCol   = [];
    this.keyCount = 0;
    this.h = this.vOffset + this.spacer;
    this.longestText = this.title.length;
  }

  draw(){
    //super.draw();
    const ctx = this.display.canvas.getContext("2d");

    // blank out background
    ctx.fillStyle = 'white';
    ctx.globalAlpha = 0.8;
    ctx.fillRect(this.x, this.y, this.w, this.h);
    ctx.globalAlpha = 1;                                        // TODO - sort propert geometry calculation out for text placement


    this.col_ink = 'black';
    this.placeText(ctx, this.title, this.x + this.spacer *2, this.y + this.vOffset, this.col_ink, this.fontSize, 'left', 'top' )

    for (let k=0; k<this.keyCount; k++){
      this.col_ink = 'black';
      this.placeText(ctx, this.keyTxt[k], this.x + this.spacer *2, this.y + this.spacer *(k+1) + this.vOffset, this.col_ink, this.fontSize, 'left', 'top' );
      ctx.fillStyle = this.keyCol[k];
      ctx.fillRect(this.x + this.spacer/2, this.y + this.spacer *(k+1) + this.vOffset, this.colRectSz, this.colRectSz);  
    }

    console.log(`w:${this.w}, h:${this.h}, spacer:${this.spacer}, vOffset:${this.vOffset}, font:${this.fontSize}`)
  }
}

class TargetBand extends DisplayObject {
  // display rolling average for period length
  constructor( {display, doName,
                alpha, fontSize, 
                col_bbox, dbgOn} = {},
                dtkChart,
                label='#',bandUpper, bandLower,
                upperInk, lowerInk, bandInk )
  {
    super({ display:display, doName:doName, 
            alpha:alpha, fontSize:fontSize, col_bbox:col_bbox, dbgOn:dbgOn});
    this.dtkChart = dtkChart;
    this.x_pc = 0;
    this.y_pc = this.dtkChart.yPcFromyVal(bandUpper);
    this.w_pc = 100;
    this.h_pc = this.dtkChart.yPcFromyVal(bandLower) - this.dtkChart.yPcFromyVal(bandUpper);   // bandUpper - bandLower        
    this.label        = label;
    this.bandUpper    = bandUpper;
    this.bandUpper_pc = this.dtkChart.yPcFromyVal(bandUpper);
    this.bandLower    = bandLower;
    this.bandLower_pc = this.dtkChart.yPcFromyVal(bandLower);

    this.upperInk   = upperInk; 
    this.lowerInk   = lowerInk; 
    this.bandInk    = bandInk;

  }  
  
  getBoundaryValues() {
    if (this.dtkChart){
      const {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange} = this.dtkChart;
      Object.assign(this, {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange});
    }
  }
  
  // 
  draw(){
    this.getBoundaryValues();
    console.log(`doName: ${this.doName}, label: ${this.label}, bandLower: ${this.bandLower}, bandUpper: ${this.bandUpper}\nyAxisMinVal: ${this.yAxisMinVal}, yAxisMaxVal: ${this.yAxisMaxVal}`);
    
    super.draw(); // this.scaleCoords();
    const ctx = this.display.canvas.getContext("2d");
    const cW = this.display.canvas.width;
    ctx.fillStyle = this.bandInk;
    ctx.globalAlpha = this.alpha * 0.2;

    ctx.fillRect(this.x, this.y, cW, this.h);

    ctx.globalAlpha = this.alpha * 0.8;

    // UPPER BAND LINE
    let xl = 0;
    let pointLabelText = `${this.bandLower.toFixed(1)} - ${this.bandUpper.toFixed(1)}`;
    let xr = 100;
    // debug text
    this.placeCentreTextNoMk(ctx, pointLabelText, xl, xr, this.y - this.fontSize *2, this.col_ink, this.fontSize, 'center', 'middle');
    
    let dsObjConfig = { display:this.display, doName:`${this.y_pc}`, 
                        x_pc:0,     y_pc:this.bandUpper_pc,
                        x1_pc:100,  y1_pc:this.bandUpper_pc,          
                        col_ink:this.upperInk, alpha:0.8, fontSize:this.fontSize,
                        col_bbox:'cyan', dbgOn:this.dbgOn};

    let uBand = new ScaledLine(dsObjConfig, [], 2);  // [] = solid line
    uBand.draw();

    // LOWER BAND LINE
    xl = 0;
    pointLabelText = `${this.bandLower.toFixed(1)} - ${this.bandUpper.toFixed(1)}`;
    xr = 100;
    // debug text
    this.placeCentreTextNoMk(ctx, pointLabelText, xl, xr, this.y - this.fontSize *2, this.col_ink, this.fontSize, 'center', 'middle');
    
    dsObjConfig = { display:this.display, doName:`${this.y_pc}`, 
                    x_pc:0,     y_pc:this.bandLower_pc,
                    x1_pc:100,  y1_pc:this.bandLower_pc,
                    col_ink:this.upperInk, alpha:0.8, fontSize:this.fontSize,
                    col_bbox:'cyan', dbgOn:this.dbgOn};

    let lBand = new ScaledLine(dsObjConfig, [], 2);  // [] = solid line
    lBand.draw();
    
    ctx.globalAlpha = 1;  // TODO - sort propert geometry calculation out for text placement
  }
}


class SummaryBar extends DisplayObject {
  static AV7_LW = 4;  // LW Line Width
  static LPAV7_LW = 2;
  static MINMAX_LW = 1;

  // display rolling average for period length
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                dtkChart, dataSourceKey )
  {
    super({ display:display, doName:doName, 
            x_pc:x_pc, y_pc:y_pc, w_pc:w_pc, h_pc:h_pc, arc_rad:arc_rad, 
            col_ink:col_ink, col_bk:col_bk, alpha:alpha, fontSize:fontSize, col_bbox:col_bbox, dbgOn:dbgOn});
    
    this.dtkChart       = dtkChart;
    this.dataSourceKey  = dataSourceKey;
    
    // max,min & ave for THIS week w/ deltas of max,min & ave for LAST week
    this.getBoundaryValues(); 
    this.calculateBands();

    console.log(`\n> - - SummaryBar:${this.dataSourceKey} <`);
    console.log(`S:${this.startIndex}, pWin:${this.periodWindow}, E:${this.endIndex}`);
    console.log(`MIN:${this.dataSourceMin}, AVE:${dtkChartData[this.endIndex]}, MAX:${this.dataSourceMax}`);
    console.log(`dataSources: ${this.dtkChart.chartSettings.selectedDataSources}`);
  }

  getBoundaryValues() {  // potentialy MANY datasources - TODO move to display object??
    if (this.dtkChart){
      const {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange} = this.dtkChart;
      Object.assign(this, {periodWindow, endIndex, startIndex, xIncrement_pc, dataMin, dataMax, yAxisMinVal, yAxisMaxVal, yAxisRange});
    }
  }

  minMaxAveForPeriod(startIndex, endIndex){
    console.log(`sBar.minMaxAveForPeriod:dataSourceKey:${this.dataSourceKey}`);
    let min = parseFloat(dtkChartData[startIndex][this.dataSourceKey]);
    let max = parseFloat(dtkChartData[startIndex][this.dataSourceKey]);
    
    let total = 0;
    let steps = endIndex - startIndex;    
    for (let i = startIndex; i < endIndex; i++){
      // console.log(`[i]: [${i}] <`);
      // console.log(dtkChartData[i]);
      let dataPoint = parseFloat(dtkChartData[i][this.dataSourceKey]);
      total += dataPoint;
      if (min > dataPoint) min = dataPoint;
      if (max < dataPoint) max = dataPoint;
    }
    let ave = (total / steps).toFixed(1);
    
    return [min, ave, max];
  }

  calculateBands(){
    [this.dataSourceMin,this.dataSourceAve,this.dataSourceMax] = this.minMaxAveForPeriod(this.startIndex, this.endIndex);
    console.log(`Min:${this.dataSourceMin} - Ave:${this.dataSourceAve} - Max:${this.dataSourceMax} - CALC`);
    // console.log(dtkChartData[this.endIndex-1]);
    // console.log(dtkChartData[this.endIndex-1][this.dataSourceKey]);
    // console.log(dtkChartData[this.endIndex-1][`${this.dataSourceKey}_av7`]);
    //console.log(`Min:${this.endIndex} - Ave:${this.endIndex} - Max:${this.endIndex} - DATA`);
    let startIndexLP  = this.startIndex - this.periodWindow;
    let endIndexLP    = this.endIndex - this.periodWindow;
    [this.dataSourceMinLP,this.dataSourceAveLP,this.dataSourceMaxLP] = this.minMaxAveForPeriod(startIndexLP, endIndexLP);

    this.dataSourceMinDelta = this.dataSourceMin - this.dataSourceMinLP;
    this.dataSourceAveDelta = this.dataSourceAve - this.dataSourceAveLP;
    this.dataSourceMaxDelta = this.dataSourceMax - this.dataSourceMaxLP;
  }

  // max, ave, min line
  drawSummaryDataLine(yVal, colInk='magenta', pattern=[], lineWidth=2){
    let y_pc = this.dtkChart.yPcFromyVal(parseFloat(yVal));

    let dsObjConfig = { display:this.display, doName:`${yVal}`, 
        x_pc:this.x_pc,               y_pc:y_pc,
        x1_pc:this.x_pc+this.w_pc,    y1_pc:y_pc,          
        col_ink:colInk, col_bk:'white', alpha:1, fontSize:this.fontSize,
        col_bbox:'cyan', dbgOn:false};
                                // linePattern, lineWidth
    let tl = new ScaledLine(dsObjConfig, pattern, lineWidth);
    tl.draw();
  }

  // vertical line w/ text next to it placed xPos_pc % across the width of the SummaryBar
  drawSummaryDataLineJoin(yValLast, yValThis, xPos_pc, colInk='magenta', pattern=[], lineWidth=2){
    let yL_pc     = this.dtkChart.yPcFromyVal(parseFloat(yValLast));    
    let yT_pc     = this.dtkChart.yPcFromyVal(parseFloat(yValThis));
    let delta     = yValLast - yValThis;
    let yText_pc  = this.dtkChart.yPcFromyVal(parseFloat(yValLast + delta/2));
        
    let dsObjConfig = { display:this.display, doName:`delta`, 
        x_pc:this.x_pc+(this.w_pc* xPos_pc/100),  y_pc:yL_pc,
        x1_pc:this.x_pc+(this.w_pc* xPos_pc/100), y1_pc:yT_pc,          
        col_ink:colInk, col_bk:'white', alpha:1, fontSize:this.fontSize,
        col_bbox:'cyan', dbgOn:false};
                                // linePattern, lineWidth
    let tl = new ScaledLine(dsObjConfig, pattern, lineWidth);
    tl.draw();
    // draw text

  }  

  draw(){
    this.getBoundaryValues(); 
    this.calculateBands();      // calculates bands for period window 7,14,28,3m etc 
    super.draw()

    console.log(`sBar.draw:dataSourceKey:${this.dataSourceKey} - ink:${this.col_ink}`);

    // weight colours
    let lineCol     = this.dtkChart.chartSettings.col_ink[`${this.dataSourceKey}_av7`];
    let minMaxCol   = this.dtkChart.chartSettings.col_ink[this.dataSourceKey];

    let ave7day     = parseFloat(dtkChartData[this.endIndex-1][`${this.dataSourceKey}_av7`]);
    let endIndexLP  = this.endIndex - 7; // - this.periodWindow; use calculateBands() for periodWindow!
    let ave7dayLP   = parseFloat(dtkChartData[endIndexLP-1][`${this.dataSourceKey}_av7`]);
    

    // data max
    this.drawSummaryDataLine(this.dataSourceMax,minMaxCol,[], SummaryBar.MINMAX_LW);    

    // current periodWindow average    
    //this.drawSummaryDataLine(this.dataSourceAve,lineCol,[], SummaryBar.AV7_LW);
    // current 7 day average
    this.drawSummaryDataLine(ave7day,lineCol,[], SummaryBar.AV7_LW);

    // periodWindow delta line    
    //this.drawSummaryDataLineJoin(this.dataSourceAve, this.dataSourceAveLP, 30,lineCol,[5,5], SummaryBar.LPAV7_LW);    
    // 7 day delta line    
    this.drawSummaryDataLineJoin(ave7day, ave7dayLP, 30,lineCol,[5,5], SummaryBar.LPAV7_LW);    

    // previous periodWindow ave    
    //this.drawSummaryDataLine(this.dataSourceAveLP, lineCol,[5,5], SummaryBar.LPAV7_LW);    
    // previous 7 day ave    
    this.drawSummaryDataLine(ave7dayLP, lineCol,[5,5], SummaryBar.LPAV7_LW);    

    // data min
    this.drawSummaryDataLine(this.dataSourceMin,minMaxCol,[], SummaryBar.MINMAX_LW);

    // this.drawSummaryDataLine(this.dataSourceMax, 'red',[],4);
    // this.drawSummaryDataLineJoin(this.dataSourceMaxLP, this.dataSourceMax, 30,'rgb(244, 61, 128)',[5,5], 2);
    // this.drawSummaryDataLine(this.dataSourceMaxLP, 'rgb(244, 61, 128)',[5,5],2);

    // this.drawSummaryDataLine(this.dataSourceAve, 'blue',[],4);
    // this.drawSummaryDataLineJoin(this.dataSourceAveLP, this.dataSourceAve, 50,'rgb(6, 136, 212)',[5,5], 2);
    // this.drawSummaryDataLine(this.dataSourceAveLP, 'pastel blue',[5,5],2);

    // this.drawSummaryDataLine(this.dataSourceMin, 'green',[],4);
    // this.drawSummaryDataLineJoin(this.dataSourceMinLP, this.dataSourceMin, 70,'yellowgreen',[5,5], 2);
    // this.drawSummaryDataLine(this.dataSourceMinLP, 'yellowgreen',[5,5],2);
  }
}

class DtkChart extends DisplayObject { // hold curent state
  constructor( {display, doName, x_pc, y_pc, w_pc, h_pc, arc_rad, col_ink, col_bk, alpha, fontSize, col_bbox, dbgOn} = {},
                settings = {} )
  {         
    super({ display:display, doName:doName, 
            x_pc:x_pc, y_pc:y_pc, w_pc:w_pc, arc_rad:arc_rad, 
            col_ink:col_ink, col_bk:col_bk, alpha:alpha, fontSize:fontSize, col_bbox:col_bbox, dbgOn:dbgOn})
    
    this.rafScheduled = false;
    this.chartSettings = {
              cnv_width: 400,       // set below TODO REMOVE on REFACTOR
              cnv_height: 400,
              startIndex: INDEX_START_DEFAULT,
              endIndex:   INDEX_END_DEFAULT,
              chartWidthDays: CHART_WIDTH_DAYS_DEFAULT,
              selectedDataSources: ['error'],// OVER WRITTEN BY caller ['dtk_weight'], //, 'dtk_kg_fat', 'dtk_kg_h2o'],
              fontSize: fontSize,
              availableDataSources: ['dtk_weight', 'dtk_pc_fat', 'dtk_pc_h2o', 'dtk_kg_fat', 'dtk_kg_h2o'],
              col_ink: {dtk_weight:     'rgb(249, 149, 43)', 
                        dtk_weight_av7: 'rgb(167, 86, 0)',  
                        dtk_pc_fat:     'rgb(229, 17, 144)',                        
                        dtk_kg_fat:     'rgb(229, 17, 144)',
                        dtk_kg_fat_av7: 'rgb(169, 0, 0)',                        
                        dtk_pc_h2o:     'rgb(0, 222, 243)', 
                        dtk_kg_h2o:     'rgb(0, 222, 243)', 
                        dtk_kg_h2o_av7: 'rgb(0, 101, 179)',                         
                        dtk_frame:      'rgb(107, 214, 0)'},
              band_ink:{dtk_weight: { top: 'rgb(200, 140, 85)', 
                                      bot: 'rgb(250, 190, 125)' }, 
                        dtk_pc_fat: { top: 'rgb(160, 55, 55)',
                                      bot: 'rgb(210, 105, 105)' },
                        dtk_kg_fat: { top: 'rgb(160, 55, 55)',
                                      bot: 'rgb(210, 105, 105)' },
                        dtk_pc_h2o: { top: 'rgb(65, 130, 180)', 
                                      bot: 'rgb(115, 180, 230)' },                         
                        dtk_kg_h2o: { top: 'rgb(65, 130, 180)', 
                                      bot: 'rgb(115, 180, 230)' }, 
                        dtk_frame:  { top:  'rgb(100, 160, 60)',
                                      bot:  'rgb(160, 210, 110)'}},
              target_band:{ dtk_weight: { top: 95.0,  // kg
                                          bot: 88.0 }, 
                            dtk_pc_fat: { top: 16.0,   // %
                                          bot: 10.0  },
                            dtk_kg_fat: { top: 15.2,   // kg
                                          bot: 8.8  },
                            dtk_pc_h2o: { top: 55.0, 
                                          bot: 45.0 }, 
                            dtk_kg_h2o: { top: 55.0, 
                                          bot: 45.0 }, 
                            dtk_frame:  { top: 18.0,
                                          bot: 22.0 } }
    };
    Object.assign(this.chartSettings, settings);

    // get ylimits of each data source so composite plots match yAxisNumbering
    this.calculateBoundaries(); // calculates above values

    // 1568764800000: {
    //   dtk_pc_fat: "38.3",
    //   dtk_pc_h2o: "44.8",
    //   dtk_rcp: {
    //     dt_date: 1568764800000,
    //     dt_date_readable: "2019 09 18",
    //     dt_day: "day",
    //   },
    //   dtk_user_info: { UUID: "x-x-x-x-xxx", name: "AGCT" },
    //   dtk_weight: "105.7",
    // }            

    this.zList = [this];

    let dsObjConfig = { display:display, doName:doName, 
                        x_pc:x_pc, y_pc:y_pc, w_pc:w_pc, arc_rad:arc_rad, 
                        col_ink:col_ink, col_bk:col_bk, alpha:alpha, fontSize:fontSize, col_bbox:col_bbox, dbgOn:dbgOn}

    // dsObjConfig = Object.assign(dsObjConfig, {doName:'a1', x_pc:10, y_pc:10, w_pc:10, h_pc:10, arc_rad:0, col_ink:'lime', col_bbox:'magenta'});
    // let a1 = new DisplayObject(dsObjConfig);
    // this.zList.push(a1);

    // dsObjConfig = Object.assign(dsObjConfig, {doName:'a2', x_pc:10, y_pc:80, w_pc:10, h_pc:10, arc_rad:0, col_ink:'yellowgreen', col_bbox:'magenta'});
    // let a2 = new DisplayObject(dsObjConfig);
    // this.zList.push(a2);

    // dsObjConfig = Object.assign(dsObjConfig, {doName:'a3', x_pc:80, y_pc:80, w_pc:10, h_pc:10, arc_rad:0, col_ink:'purple', col_bbox:'magenta'});
    // let a3 = new DisplayObject(dsObjConfig);
    // this.zList.push(a3);

    // dsObjConfig = Object.assign(dsObjConfig, {doName:'a4', x_pc:80, y_pc:10, w_pc:10, h_pc:10, arc_rad:0, col_ink:'orangered', col_bbox:'magenta'});
    // let a4 = new DisplayObject(dsObjConfig);
    // this.zList.push(a4);

    dsObjConfig = { display:display, doName:'vBarS', 
                    x_pc:0, y_pc:0, w_pc:100, h_pc:100, arc_rad:0, 
                    col_ink:'orangeRed', col_bk:col_bk, alpha:alpha, 
                    fontSize:this.chartSettings.fontSize, col_bbox:'purple', dbgOn:true}
    let verticalLabelBars = new VertLabelBars(dsObjConfig, this);
    this.zList.push(verticalLabelBars);

    dsObjConfig = { display:display, doName:'key', 
                    x_pc:5, y_pc:5, w_pc:30, h_pc:15, arc_rad:0, 
                    col_ink:'orangeRed', col_bk:col_bk, alpha:alpha,
                    fontSize:this.chartSettings.fontSize+2, col_bbox:'purple', dbgOn:false}
    let chartKey = new ChartKey(dsObjConfig, this, 'KEY');
    // push onto zList at end

    for (let dsIdx = 0; dsIdx < this.chartSettings.selectedDataSources.length; dsIdx++) {
      let dataSourceKey = this.chartSettings.selectedDataSources[dsIdx];

      let dataSourceInk = this.chartSettings.col_ink[dataSourceKey];

      dsObjConfig = { display:display, doName:'pData', 
                      x_pc:0, y_pc:0, w_pc:100, h_pc:100, arc_rad:0, 
                      col_ink:dataSourceInk, col_bk:col_bk, alpha:alpha, fontSize:this.chartSettings.fontSize,
                      col_bbox:'purple', dbgOn:false}

      let singlePlot = new DataPlot(dsObjConfig, this, dataSourceKey, 'test label');
      this.zList.push(singlePlot);
      chartKey.addKey(dataSourceKey, dataSourceInk)
      //chartKey.addKey(singlePlot.label, dataSourceInk)

      if (!dataSourceKey.includes('_av7')){ // only create SummaryBar for main datasource not the 7 day average
        dsObjConfig = { display:display, doName:'sBar', 
                        //x_pc:80, y_pc:0, w_pc:20, h_pc:100, arc_rad:0, 
                        x_pc:94, y_pc:0, w_pc:6, h_pc:100, arc_rad:0, 
                        col_ink:dataSourceInk, col_bk:col_bk, alpha:alpha,
                        fontSize:fontSize, col_bbox:'rgb(0, 40, 119)', dbgOn:false}

        let sBar = new SummaryBar(dsObjConfig, this, dataSourceKey);
        this.zList.push(sBar);      
      }

      if (dataSourceKey in this.chartSettings.target_band) { // add the target band
        dsObjConfig = { display:display, doName:'tBand', 
                        col_ink:dataSourceInk, col_bk:col_bk, alpha:1, fontSize:this.chartSettings.fontSize,
                        col_bbox:'purple', dbgOn:false}

        let targetBand = new TargetBand(dsObjConfig, this, `tBand:${dataSourceKey}`,
        this.chartSettings.target_band[dataSourceKey].top, this.chartSettings.target_band[dataSourceKey].bot,
        this.chartSettings.band_ink[dataSourceKey].top, this.chartSettings.band_ink[dataSourceKey].bot,
        this.chartSettings.band_ink[dataSourceKey].bot);

        this.zList.push(targetBand);
      }
                  
    }
    
    dsObjConfig = { display:display, doName:'yAxNum', 
                    x_pc:0, y_pc:0, w_pc:15, h_pc:100, arc_rad:0, 
                    col_ink:'black', col_bk:col_bk, alpha:0.5, fontSize:this.chartSettings.fontSize, col_bbox:'orange'}
    let yAxisNumbering = new YAxisNumbering(dsObjConfig, this);
    this.zList.push(yAxisNumbering);  

    this.zList.push(chartKey);

  } // olive navy maroon lime

  calculateBoundaries() {
    // scan data for min & max to scale data
    this.periodWindow   = this.chartSettings.chartWidthDays;    
    this.endIndex       = this.chartSettings.endIndex;
    this.startIndex     = this.endIndex - this.periodWindow;
    this.xIncrement_pc  = (100 / this.periodWindow);


    this.dataMax      = parseFloat(dtkChartData[this.startIndex][this.chartSettings.selectedDataSources[0]]);
    this.dataMin      = parseFloat(dtkChartData[this.startIndex][this.chartSettings.selectedDataSources[0]]);
    this.yAxisMaxVal  = null;
    this.yAxisMinVal  = null;
    this.yAxisRange   = null;

    // iterate through datasources to calculate composite limits/boundaries
    for (let dsIdx = 0; dsIdx < this.chartSettings.selectedDataSources.length; dsIdx++) {
      let dataSourceKey = this.chartSettings.selectedDataSources[dsIdx];
      
      let min = parseFloat(dtkChartData[this.startIndex][dataSourceKey]);
      let max = parseFloat(dtkChartData[this.startIndex][dataSourceKey]);
      
      for (let i = this.startIndex; i < this.endIndex; i++){
        // console.log(`[i]: [${i}] <`);
        // console.log(dtkChartData[i]);
        let dataPoint = parseFloat(dtkChartData[i][dataSourceKey]);
        if (min > dataPoint) min = dataPoint;
        if (max < dataPoint) max = dataPoint;
      }

      if (this.dataMin > min) this.dataMin = min;
      if (this.dataMax < max) this.dataMax = max;

      let dataRange = this.dataMax - this.dataMin;
      
      this.yAxisMaxVal  = this.dataMax + (0.1 * dataRange); 
      this.yAxisMinVal  = this.dataMin - (0.2 * dataRange); // 0.3 instead of 0.1 to allow for labelling
      this.yAxisRange   = this.yAxisMaxVal - this.yAxisMinVal;
    }

    console.log(`periodWindow: ${this.periodWindow}\tstartIndex:  ${this.startIndex}\tthis.endIndex: ${this.endIndex}`);
    console.log(`dataMax:      ${this.dataMax}\tyAxisMaxVal: ${this.yAxisMaxVal}`);
    console.log(`dataMin:      ${this.dataMin}\tyAxisMinVal: ${this.yAxisMinVal}`);
    // console.log(`myvar:${myvar}`);
  }

  // call getBoundaryValues() before this! 
  yPcFromyVal(yVal){
    let yPosFromRangeMin = yVal - this.yAxisMinVal; 

    // this.yAxisRange (range 104.0 to 108.0) range = 4.0
    let yPosFromMin_pc  = (yPosFromRangeMin / this.yAxisRange) * 100;   

     // 100 - y_pc to invert because 0,0 is at the top!
    let y_pc  = 100 - yPosFromMin_pc;

    return y_pc;
  };  

  update(){
    this.calculateBoundaries();
    this.display.sync(this);
  }

  resizeCanvas(){
    // Get the new window dimensions
    const winInnerWidth = window.innerWidth;
    const winInnerHeight = window.innerHeight;

    // Resize the canvas to the new dimensions
    this.display.canvas.width = winInnerWidth;
    this.display.canvas.height = winInnerHeight / 2;
    //this.display.canvas.style.position = 'absolute';
    this.display.canvas.style.left = "0px";        
    this.update();
    this.rafScheduled = false;
  }

  addDisplayObject(dspObj){
    this.zList.push(dspObj);
  }
}
	




class Canvas {
  constructor(parent = document.body, width = 400, height = 400) {
    console.log(`Canvas:\nparent: ${parent}`);
    this.canvas = document.createElement('canvas');
    this.canvas.width = width;
    this.canvas.height = height;
    //this.canvas.style.position = 'absolute';
    //this.canvas.style.top = "100px";
    this.canvas.style.left = "0px";    
    parent.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
  }

  sync(dtkChart) {
    this.clearDisplay();
    this.update(dtkChart.zList);
  }

  clearDisplay() {
    // opacity controls the trail effect in animation set to 1 to remove
    //this.ctx.fillStyle = 'rgba(255, 255, 255, .4)';
    this.ctx.fillStyle = 'rgba(255, 255, 255, 1)';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.strokeStyle = 'black';
    this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);
  }

  update(zList){
    for (let dspObj of zList){
      dspObj.draw();
    }
  }

}


export class DtkChartWithControls { 
  constructor( chartName, parentDivId, settings = {} )
  {
    // TODO get settings
    settings.cnv_width = 400;
    settings.cnv_height = 400;
    
    // create html - controls
    this.canvasDivId = `${chartName}-dtk-chart-canv`;
    this.createChartHtml(chartName, parentDivId);

    // add chart
    this.parentDivId = parentDivId;     
    console.log(`DtkChartWithControls: N:${this.chartName} C:${this.canvasDivId} P:${this.parentDivId}`)

    const canvasParent = document.getElementById(this.canvasDivId);
    this.display = new Canvas(canvasParent, settings.cnv_width, settings.cnv_height);
    this.display.canvas.width = window.innerWidth;
    this.display.canvas.height = settings.cnv_height;

    this.dtkChart = new DtkChart(  
      { display: this.display,
        doName:'dtkProgress',
        x:0, y:0, w:settings.cnv_width, h:settings.cnv_height,
        col_ink:'black', col_bk:'white', alpha:'100', fontSize:10, col_bbox:'olive', dbgOn:true },
        settings ) ;

    this.dtkChart.update(); // pass in state: 7day, 14d, 21d, 1m, 3m, 6m, 1y, 2y, plus new dimensions

    var periodWindowButtons = document.getElementById(`${chartName}-btn-period-window`);
    periodWindowButtons.addEventListener('click', (e) => this.processUIPeriodButtonEvents(e));

    // When you pass rafResizeCanvas to requestAnimationFrame, it’s being called without the context of 
    // DtkChartWithControls instance, so this inside resizeCanvas doesn’t refer to the DtkChart - bind(the object!)
    const rafResizeCanvas = this.dtkChart.resizeCanvas.bind(this.dtkChart);

    window.addEventListener('resize', () => {
      //rafResizeCanvas();              // work is bind is used above
      //this.dtkChart.resizeCanvas();   // works because arrow function uses this from external context - 'lexically bound'
      if (this.dtkChart.rafScheduled === false) {
        this.dtkChart.rafScheduled = true;
        requestAnimationFrame(rafResizeCanvas);
      }
    });
    
  }

  createChartHtml(chartName, parent) {
    this.chartName = chartName.toLowerCase();
    var html = `
    <div id="${this.chartName}-btn-period-window" class="d-inline-flex w-100">
        <div class="btn-group btn-group-toggle" data-toggle="buttons">
            <label class="btn btn-secondary period-window">
                <input type="radio" name="options" value="7" id="${this.chartName}-but-win-set-7d" autocomplete="off">7D
            </label>
            <label class="btn btn-secondary period-window">
                <input type="radio" name="options" value="14" id="${this.chartName}-but-win-set-14d" autocomplete="off">14D
            </label>
            <label class="btn btn-secondary period-window">
                <input type="radio" name="options" value="28" id="${this.chartName}-but-win-set-28d" autocomplete="off">1M
            </label>
            <label class="btn btn-secondary period-window">
                <input type="radio" name="options" value="88" id="${this.chartName}-but-win-set-3m" autocomplete="off">3M
            </label>
            <label class="btn btn-secondary period-window">
                <input type="radio" name="options" value="176" id="${this.chartName}-but-win-set-6m" autocomplete="off">6M
            </label>
            <label class="btn btn-secondary period-window">
                <input type="radio" name="options" value="0" id="${this.chartName}-but-win-set-0" autocomplete="off">All
            </label>
        </div>
        <inline class="bt-nav-space"></inline>
        <div class="btn-group ml-3">
            <button id="${this.chartName}-but-win-mov-bak" type="button" class="btn btn-outline-secondary"><</button>
            <button id="${this.chartName}-but-win-mov-fwd" type="button" class="btn btn-outline-secondary">></button>
        </div>
    </div>
    <div id="${this.canvasDivId}"></div>`;

    var div = document.createElement('div');
    div.id = `${this.chartName}-chrt-cont`;
    div.innerHTML = html;
    //document.getElementById(parent).appendChild(div.firstChild);
    document.getElementById(parent).appendChild(div);
  }

  isPeriodWindowSizeButton(e){
    if (e.target.children.length > 0) {
      return e.target.children[0].id.includes('but-win-set'); 
    } else {
      return false;
    }
  }

  periodWindowSize(e){
    return e.target.children[0].value
  }

  processUIPeriodButtonEvents(e) {
      console.log(`periodWindowButtons: ${e.target.id}`);
      console.log(e.target.value);
      console.log(e.target);
      if (this.isPeriodWindowSizeButton(e)){
        if (this.dtkChart.chartSettings.chartWidthDays != this.periodWindowSize(e)){ // no repaint unless needed
            this.dtkChart.chartSettings.chartWidthDays = this.periodWindowSize(e);        
            console.log(`chSetgs.chartWidthDays: ${this.dtkChart.chartSettings.chartWidthDays}`);
            this.dtkChart.update();
            return
        }
      }         
      if (e.target.id === `${this.chartName}-but-win-mov-fwd`){
          console.log(`chSetgs.endIndex: ${this.dtkChart.chartSettings.endIndex} + this.dtkChart.chartSettings.chartWidthDays:${this.dtkChart.chartSettings.chartWidthDays}`);
          this.dtkChart.chartSettings.endIndex = parseInt(this.dtkChart.chartSettings.endIndex) + parseInt(this.dtkChart.chartSettings.chartWidthDays);
          console.log(`chSetgs.endIndex AFTER ADD: ${this.dtkChart.chartSettings.endIndex}`);
          
          if (this.dtkChart.chartSettings.endIndex > dtkChartData.length){
              this.dtkChart.chartSettings.endIndex = dtkChartData.length;
              this.dtkChart.chartSettings.startIndex = this.dtkChart.chartSettings.endIndex - this.dtkChart.chartSettings.chartWidthDays;
          }            
          
          console.log(`chSetgs.endIndex: ${this.dtkChart.chartSettings.endIndex}`);
          this.dtkChart.update();
          return
      }
      if (e.target.id === `${this.chartName}-but-win-mov-bak`){        
          console.log(`chSetgs.endIndex: ${this.dtkChart.chartSettings.endIndex} + this.dtkChart.chartSettings.chartWidthDays:${this.dtkChart.chartSettings.chartWidthDays}`);
          this.dtkChart.chartSettings.endIndex = parseInt(this.dtkChart.chartSettings.endIndex) - parseInt(this.dtkChart.chartSettings.chartWidthDays);
          console.log(`chSetgs.endIndex AFTER SUB: ${this.dtkChart.chartSettings.endIndex}`);
  
          if (parseInt(this.dtkChart.chartSettings.startIndex) < 0 ){
              this.dtkChart.chartSettings.startIndex = 0;
              this.dtkChart.chartSettings.endIndex = this.dtkChart.chartSettings.chartWidthDays;
          }
  
          console.log(`chSetgs.endIndex: ${this.dtkChart.chartSettings.endIndex}`);
          this.dtkChart.update();
          return
      }   
  };
}


