import hype.*;
import hype.extended.behavior.*;
import hype.extended.colorist.*;
import hype.extended.layout.*;
import hype.interfaces.*;
import themidibus.*;

HGroup pads;
HDrawable clicked;
MidiBus midiBus;
HashMap<Integer, Integer> colorMap;
void setup() {
  frameRate(5); // 5 FPS should be fine
  size(450, 450);
  H.init(this).background(#202020).autoClear(true);
  smooth();
  colorMap = new HashMap<Integer, Integer>();
  colorMap.put(0, color(#ffffff)); // Off
  colorMap.put(1, color(#FF9595)); // DimRed
  colorMap.put(2, color(#FF4B4B)); // Red
  colorMap.put(3, color(#FC0000)); // BrightRed
  colorMap.put(16, color(#B7FFBC)); // DimGreen
  colorMap.put(32, color(#4CE557)); // Green
  colorMap.put(48, color(#1AFF2A)); // BrightGreen
  colorMap.put(17, color(#FDFFC9)); // DimYellow
  colorMap.put(34, color(#F1F755)); // Yellow
  colorMap.put(51, color(#F6FF00)); // BrightYellow
  colorMap.put(18, color(#FFD493)); // DimOrange
  colorMap.put(19, color(#FF6C3B)); // RedOrange
  colorMap.put(35, color(#FF9900)); // Orange
  colorMap.put(33, color(#ECFF83)); // DimGreenYellow
  colorMap.put(49, color(#D7FA51)); // GreenYellow
  colorMap.put(50, color(#ECFF71)); // YellowGreen

  pads = H.add(new HGroup());

  for (int i = 0; i < 9; i++) {
    for (int j = 0; j < 9; j++) {
      if (i != 0 || j != 8) {
        HBundle metadata = new HBundle().num("row", i).num("col", j);
        // Add ovals for modifier pads
        if (i == 0 || j == 8) {
          HEllipse oval = new HEllipse(25, 20);
          oval.strokeWeight(2).stroke(#181818).fill(#ffffff).extras(metadata).loc(j * 50, i * 50 + 5);
          pads.add(oval);
        } else {
          HRect rect = new HRect(50, 50).rounding(8);
          rect.strokeWeight(2).stroke(#181818).fill(#ffffff).extras(metadata).loc(j * 50, i * 50);
          pads.add(rect);
        }
      }
    }
  }
  MidiBus.list();
  midiBus = new MidiBus(this, "Processing", "CMD Touch");
}

boolean clickToggle = false;
boolean printToggle = false;
void draw() {

  if (clickToggle && !printToggle && clicked != null) {
    int row = (int) clicked.num("row");
    int col = (int) clicked.num("col");
    int pad = getPad(row, col);
    midiBus.sendNoteOn(0, pad, 127);
    printToggle = true;
  }
  if (!clickToggle && printToggle && clicked != null) {
    int row = (int) clicked.num("row");
    int col = (int) clicked.num("col");
    int pad = getPad(row, col);
    midiBus.sendNoteOff(0, pad, 0);
    printToggle = false;
  }
  H.drawStage();
}


void mousePressed() {
  clickToggle = true;
  for (HDrawable d : pads) {
    if (d.contains(mouseX, mouseY)) {
      clicked = d;
    }
  }
}

void mouseReleased() {
  clickToggle = false;
}

void noteOn(int channel, int pitch, int velocity) {
  HDrawable pad = getObject(pitch);
  pad.fill(colorMap.get(velocity));
}

void noteOff(int channel, int pitch, int velocity) {
  HDrawable pad = getObject(pitch);
  pad.fill(colorMap.get(velocity));
}


private int getPad(int row, int col) {
  return (row * 12) + col + 12;
}

private HDrawable getObject(int pad) {
  for (HDrawable hd : pads) {
    int row = (int) hd.num("row");
    int col = (int) hd.num("col");
    if (getPad(row, col) == pad) {
      return hd;
    }
  }
  return null;
}