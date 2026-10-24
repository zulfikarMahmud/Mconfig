# -*- coding: utf-8 -*-
"""
elliptical_lift_distribution.png  generator for the M-config wing.
- Auto-locates the case project dir (the folder holding Input_Datas/Output_Datas)
  by walking up from this script's location.
- Reads design parameters from Input_Datas/input.in (SPAN, HSPAN_INNER, MACH,
  atmosphere DEN/SSP, AOA/CL design point, config switches).
- Reads results from Output_Datas: LIFT_SPAN.dat (span load), WBCAero.out
  (lift force, reference area), polar.dat (actual run CL).
- Plots the exact elliptic target  l(y)=l0*sqrt(1-(2y/b)^2)  with the same
  total lift as the actual run, overlaid with the actual span load.
Pure-stdlib PNG rasterizer (no matplotlib/Pillow).
"""
import math, struct, zlib, os, sys, time

# ---------------------------------------------------------------- PNG writer
def write_png(path, width, height, pixels):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += pixels[y]
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
        return c
    blob = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))
    for attempt in range(4):
        try:
            with open(path, "wb") as f:
                f.write(blob)
            return
        except OSError as e:
            if attempt < 3:
                time.sleep(0.6)     # file may be briefly locked (viewer/antivirus)
            else:
                raise e

# ------------------------------------------------- 5x7 bitmap font (MSB=top)
F = {
' ':[0,0,0,0,0],'!':[0,0,0x5f,0,0],'(': [0,0x1c,0x22,0x41,0],')':[0,0x41,0x22,0x1c,0],
',':[0,0x40,0x20,0,0],'-':[0,0x08,0x08,0x08,0],'.':[0,0,0,0x40,0],'/':[0x40,0x20,0x10,0x08,0x04],
'0':[0x3e,0x51,0x49,0x45,0x3e],'1':[0,0x42,0x7f,0x40,0],'2':[0x42,0x61,0x51,0x49,0x46],
'3':[0x21,0x41,0x45,0x4b,0x31],'4':[0x18,0x14,0x12,0x7f,0x10],'5':[0x27,0x45,0x45,0x45,0x39],
'6':[0x3c,0x4a,0x49,0x49,0x30],'7':[0x01,0x71,0x09,0x05,0x03],'8':[0x36,0x49,0x49,0x49,0x36],
'9':[0x06,0x49,0x49,0x29,0x1e],':':[0,0x36,0,0,0],';':[0,0x56,0x20,0,0],'=':[0,0x14,0x14,0x14,0],
'+':[0,0x08,0x3e,0x08,0],'>':[0,0x22,0x14,0x08,0],'<':[0,0x08,0x14,0x22,0],'*':[0,0x14,0x08,0x14,0],
'A':[0x7c,0x12,0x11,0x12,0x7c],'B':[0x7f,0x49,0x49,0x49,0x36],'C':[0x3e,0x41,0x41,0x41,0x22],
'D':[0x7f,0x41,0x41,0x22,0x1c],'E':[0x7f,0x49,0x49,0x49,0x41],'F':[0x7f,0x09,0x09,0x09,0x01],
'G':[0x3e,0x41,0x49,0x49,0x7a],'H':[0x7f,0x08,0x08,0x08,0x7f],'I':[0,0x41,0x7f,0x41,0],
'J':[0x20,0x40,0x41,0x3f,0x01],'K':[0x7f,0x08,0x14,0x22,0x41],'L':[0x7f,0x40,0x40,0x40,0x40],
'M':[0x7f,0x02,0x0c,0x02,0x7f],'N':[0x7f,0x04,0x08,0x10,0x7f],'O':[0x3e,0x41,0x41,0x41,0x3e],
'P':[0x7f,0x09,0x09,0x09,0x06],'Q':[0x3e,0x41,0x51,0x21,0x5e],'R':[0x7f,0x09,0x19,0x29,0x46],
'S':[0x46,0x49,0x49,0x49,0x31],'T':[0x01,0x01,0x7f,0x01,0x01],'U':[0x3f,0x40,0x40,0x40,0x3f],
'V':[0x1f,0x20,0x40,0x20,0x1f],'W':[0x3f,0x40,0x38,0x40,0x3f],'X':[0x63,0x14,0x08,0x14,0x63],
'Y':[0x07,0x08,0x70,0x08,0x07],'Z':[0x61,0x51,0x49,0x45,0x43],
'a':[0x20,0x54,0x54,0x54,0x78],'b':[0x7f,0x48,0x44,0x44,0x38],'c':[0x38,0x44,0x44,0x44,0x20],
'd':[0x38,0x44,0x44,0x48,0x7f],'e':[0x38,0x54,0x54,0x54,0x18],'f':[0x08,0x7e,0x09,0x01,0x02],
'g':[0x0c,0x52,0x52,0x52,0x3e],'h':[0x7f,0x08,0x04,0x04,0x78],'i':[0,0x44,0x7d,0x40,0],
'j':[0x20,0x40,0x44,0x3d,0],'k':[0x7f,0x10,0x28,0x44,0],'l':[0,0x41,0x7f,0x40,0],
'm':[0x7c,0x04,0x18,0x04,0x78],'n':[0x7c,0x08,0x04,0x04,0x78],'o':[0x38,0x44,0x44,0x44,0x38],
'p':[0x7c,0x14,0x14,0x14,0x08],'q':[0x08,0x14,0x14,0x18,0x7c],'r':[0x7c,0x08,0x04,0x04,0x08],
's':[0x48,0x54,0x54,0x54,0x20],'t':[0x04,0x3f,0x44,0x40,0x20],'u':[0x3c,0x40,0x40,0x20,0x7c],
'v':[0x1c,0x20,0x40,0x20,0x1c],'w':[0x3c,0x40,0x30,0x40,0x3c],'x':[0x44,0x28,0x10,0x28,0x44],
'y':[0x0c,0x50,0x50,0x50,0x3c],'z':[0x44,0x64,0x54,0x4c,0x44],
}

# ------------------------------------------------------------------- canvas
W, H = 1420, 900
BLACK=(18,18,18); GRID=(205,205,205); BLUE=(0,100,200); RED=(215,60,50)
LGRAY=(244,244,244); DK=(120,120,120)
img = [bytearray(b'\xff\xff\xff')*W for _ in range(H)]

def setp(x,y,c):
    if 0<=x<W and 0<=y<H: img[y][x*3:x*3+3]=bytes(c)

def line(x0,y0,x1,y1,c,t=1):
    dx=abs(x1-x0); dy=-abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1
    err=dx+dy
    while True:
        for ox in range(-(t//2),(t-1)//2+1):
            for oy in range(-(t//2),(t-1)//2+1): setp(x0+ox,y0+oy,c)
        if x0==x1 and y0==y1: break
        e2=2*err
        if e2>=dy: err+=dy; x0+=sx
        if e2<=dx: err+=dx; y0+=sy

def text(x,y,s,c,scale=2):
    cx=x
    for ch in s:
        g=F.get(ch,F[' '])
        for col in range(5):
            b=g[col]
            for row in range(7):
                if b & (1<<row):   # bit 0 = top row
                    for ox in range(scale):
                        for oy in range(scale): setp(cx+col*scale+ox, y+row*scale+oy, c)
        cx+=6*scale

def text_v(x,y,s,c,scale=2):   # vertical (top->bottom), for y-axis name
    cy=y
    for ch in s:
        g=F.get(ch,F[' '])
        for col in range(5):
            b=g[col]
            for row in range(7):
                if b & (1<<row):   # bit 0 = top row
                    for ox in range(scale):
                        for oy in range(scale): setp(x+col*scale+ox, cy+row*scale+oy, c)
        cy+=8*scale

def rect(x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): setp(x,y,c)

# ------------------------------------------------------- file discovery
def find_project_dir(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d,"Input_Datas")) and os.path.isdir(os.path.join(d,"Output_Datas")):
            return d
        parent = os.path.dirname(d)
        if parent == d: return None
        d = parent

# ------------------------------------------------------------- parsers
def num_tokens(text):
    out=[]
    for t in text.split():
        try: out.append(float(t))
        except ValueError: pass
    return out

def parse_input_in(path):
    p={}
    with open(path,"r",encoding="utf-8",errors="replace") as f:
        lines=f.readlines()
    def after(header_kw, n):
        for i,ln in enumerate(lines):
            if "[" in ln and all(k in ln for k in header_kw):
                # next non-empty line
                for j in range(i+1,len(lines)):
                    if lines[j].strip():
                        toks=num_tokens(lines[j])
                        if len(toks)>=n: return toks[:n]
                        break
        return None
    # CASE / config switches (POST SWITCH NACELLE H_Tail V_Tail Fuse.V)
    cfg = after(["POST","SWITCH"],6)
    if cfg: p["POST"],p["SWITCH"],p["NACELLE"],p["H_Tail"],p["V_Tail"],p["FuseV"] = [int(v) for v in cfg]
    # atmosphere DEN PRE SSP COV
    at = after(["DEN","PRE","SSP"],4)
    if at: p["DEN"],p["PRE"],p["SSP"],p["COV"] = at
    # design status ICL DCLDA ALPHA0
    ds = after(["ICL","DCLDA"],3)
    if ds: p["ICL"],p["DCLDA"],p["ALPHA0"] = int(ds[0]), ds[1], ds[2]
    # state MACH AOA/CL REY
    st = after(["MACH","AOA/CL","REY"],3)
    if st: p["MACH"],p["AOA/CL"],p["REY"] = st
    # planform SPAN HSPAN_INNER AREA_REF TAPER ROOTCHD SWEEP_LE
    pl = after(["SPAN","HSPAN_INNER"],6)
    if pl: p["SPAN"],p["HSPAN_INNER"],p["AREA_REF"],p["TAPER"],p["ROOTCHD"],p["SWEEP_LE"] = pl
    return p

def parse_wbcaero_out(path):
    lift=sref=None
    with open(path,"r",errors="replace") as f:
        lines=f.readlines()
    for i,ln in enumerate(lines):
        if "LIFT(N)" in ln and i+1<len(lines):
            toks=num_tokens(lines[i+1])
            if toks: lift=toks[0]
        if "Reference Area" in ln and i+1<len(lines):
            toks=num_tokens(lines[i+1])
            if toks: sref=toks[0]
    return lift, sref

def parse_polar(path):
    # VARIABLES=AOA,Ma,Re,Cl,Cd,CM,CLD,CDFP,CDIND,CDWAVE ; data line after ZONE
    with open(path,"r",errors="replace") as f:
        lines=f.readlines()
    for ln in lines:
        t=ln.strip()
        if t and not t.startswith("#") and not t.startswith("VARIABLES") and not t.startswith("ZONE"):
            toks=num_tokens(t)
            if len(toks)>=5:
                return toks[0], toks[1], toks[2], toks[3], toks[4]  # AOA,Ma,Re,Cl,Cd
    return None

def read_lift_span(path):
    ys,ls=[],[]
    with open(path,"r") as f:
        for ln in f:
            t=ln.strip()
            if not t or t.startswith("#"): continue
            toks=t.split()
            if len(toks)>=2:
                try: ys.append(float(toks[0])); ls.append(float(toks[1]))
                except ValueError: pass
    return ys,ls

# ------------------------------------------------------------- main
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj = find_project_dir(script_dir)
    if proj is None:
        print("ERROR: could not locate a folder with Input_Datas/Output_Datas "
              "by walking up from", script_dir); sys.exit(1)
    inp_file = os.path.join(proj,"Input_Datas","input.in")
    lift_file= os.path.join(proj,"Output_Datas","LIFT_SPAN.dat")
    wbc_file = os.path.join(proj,"Output_Datas","WBCAero.out")
    pol_file = os.path.join(proj,"Output_Datas","polar.dat")
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"elliptical_lift_distribution.png")

    p = parse_input_in(inp_file)
    lift, sref = parse_wbcaero_out(wbc_file)
    pol = parse_polar(pol_file)
    act_y, act_l = read_lift_span(lift_file)

    if not p.get("SPAN") or not lift or not sref:
        print("ERROR: missing essential data (SPAN/lift/sref).")
        print("input keys:", p); print("lift,sref:",lift,sref); sys.exit(1)

    SPAN = p["SPAN"]; HSPAN = SPAN/2.0
    MACH = p.get("MACH"); CL_in = p.get("AOA/CL"); REY = p.get("REY")
    HSPAN_INNER = p.get("HSPAN_INNER")
    cl_run = pol[3] if pol else (p.get("AOA/CL") or 0.5)
    aoa_run = pol[0] if pol else 0.0
    cd_run  = pol[4] if pol else 0.0

    # ---- elliptical target anchored to the WING's own load over the loaded span ----
    # The inboard region y in [0, ys0) lies inside the fuselage (not a lifting
    # surface), so it must NOT contribute to the target total. Prandtl's
    # min-induced-drag ellipse is fitted to carry exactly the wing's integrated
    # load over [ys0, ys1]; the inboard part is shown dashed only as reference.
    ys0 = min(act_y); ys1 = max(act_y)          # actual loaded span (root station..tip)
    A_half = 0.0                                 # wing lift integral over [ys0,ys1], half-span
    for i in range(len(act_y)-1):
        A_half += 0.5*(act_l[i]+act_l[i+1])*(act_y[i+1]-act_y[i])
    full_total = 2.0*A_half
    def shape_area(a, b_, bb):
        # integral of sqrt(1-(2y/bb)^2) dy from a to b_  (bb = full span)
        u0=2.0*a/bb; u1=2.0*b_/bb
        f=lambda u: 0.5*(u*math.sqrt(max(0.0,1.0-u*u))+math.asin(u))
        return (bb/2.0)*(f(u1)-f(u0))
    L0 = A_half / shape_area(ys0, ys1, SPAN)    # ellipse peak (at centerline y=0), N/m

    YMAX = max(max(act_l) if act_l else 0, L0) * 1.15
    # round YMAX up to a nice value
    step = 10000.0 if YMAX < 60000 else 20000.0
    YMAX = math.ceil(YMAX/step)*step
    stale_note = ""

    cfg = []
    if p.get("NACELLE"): cfg.append("nacelle")
    if p.get("H_Tail"):  cfg.append("htail")
    if p.get("V_Tail"):  cfg.append("vtail")
    cfg_s = "+".join(cfg) if cfg else ""

    # ---------------- geometry
    PL, PR, PT, PB = 185, W-60, 120, H-115
    def px(x): return PL + (x/HSPAN)*(PR-PL)
    def py(v): return PT + (1 - v/YMAX)*(PB-PT)

    # ---------------- draw
    text(PL, 20, "Target Elliptical Lift Distribution - M-config Wing", BLACK, 4)
    sub = "b = %.2f m   Ma = %.3f   CL = %.3f   Re = %.0e   Sref = %.2f m^2" % (
        SPAN, MACH or 0.0, cl_run, REY or 0.0, sref)
    if cfg_s: sub += "   [ %s ]" % cfg_s
    text(PL, 66, sub, DK, 3)

    # grid
    for xt in [0,5,10,15,20,25,29]:
        x=px(xt); line(int(x),PT,int(x),PB,GRID,1)
    yticks=[]
    v=0.0
    while v<=YMAX+1:
        yticks.append(v); v+=step
    for vt in yticks:
        y=py(vt); line(PL,int(y),PR,int(y),GRID,1)
    # axes
    line(PL,PT,PR,PT,BLACK,2); line(PL,PB,PR,PB,BLACK,2)
    line(PL,PT,PL,PB,BLACK,2); line(PR,PT,PR,PB,BLACK,2)
    # x ticks
    xend = int(HSPAN)
    for xt in list(range(0,xend,5))+[xend]:
        x=px(xt); line(int(x),PB,int(x),PB+7,BLACK,1)
        text(int(x)-6*len(str(xt)), PB+14, str(xt), BLACK, 3)
    # y ticks (kN/m)
    for vt in yticks:
        y=py(vt); line(PL-8,int(y),PL,int(y),BLACK,1)
        lab = str(int(vt/1000)) if vt>0 else "0"
        text(PL-14-6*3*len(lab), int(y)-8, lab, BLACK, 3)
    # kink
    if HSPAN_INNER:
        line(int(px(HSPAN_INNER)),PT,int(px(HSPAN_INNER)),PB,DK,1)
        text(int(px(HSPAN_INNER))+8, PT+8, "kink", DK, 3)

    # curves
    n=700
    def ellv(yy): return L0*math.sqrt(max(0.0,1-(2*yy/SPAN)**2))
    # dashed: inboard portion inside the fuselage, y in [0, ys0] (reference only, not counted)
    FUSE_DASH = (150,150,200)
    seg=20
    for i in range(seg):
        a=(ys0)*i/seg; b=(ys0)*(i+1)/seg
        if i%2==0: line(int(px(a)),int(py(ellv(a))),int(px(b)),int(py(ellv(b))),FUSE_DASH,2)
    # solid: the actual target over the loaded span [ys0, ys1]
    for i in range(n):
        ya0=ys0+(ys1-ys0)*i/n; ya1=ys0+(ys1-ys0)*(i+1)/n
        line(int(px(ya0)),int(py(ellv(ya0))),int(px(ya1)),int(py(ellv(ya1))),BLUE,3)
    for i in range(len(act_y)-1):
        line(int(px(act_y[i])),int(py(act_l[i])),int(px(act_y[i+1])),int(py(act_l[i+1])),RED,2)
    for yv,lv in zip(act_y,act_l):
        x=int(px(yv)); y=int(py(lv))
        for ox in range(-3,4):
            for oy in range(-3,4):
                if ox*ox+oy*oy<=9: setp(x+ox,y+oy,RED)

    # legend (readable, scale 3) - 3 rows
    lx0,ly0,lx1,ly1 = PR-430, PT+20, PR-16, PT+132
    rect(lx0,ly0,lx1,ly1,LGRAY)
    for X0,Y0,X1,Y1 in ((lx0,ly0,lx1,ly0),(lx0,ly0,lx0,ly1),(lx1,ly0,lx1,ly1),(lx0,ly1,lx1,ly1)):
        line(X0,Y0,X1,Y1,BLACK,1)
    # row1: solid target
    line(lx0+18,ly0+22,lx0+64,ly0+22,BLUE,3)
    text(lx0+76,ly0+10,"Elliptic target (loaded-span ideal, CL=%.3f)"%cl_run,BLACK,3)
    # row2: dashed fuselage region
    for i in range(6):
        if i%2==0: line(lx0+18+i*8,ly0+62,lx0+26+i*8,ly0+62,FUSE_DASH,2)
    text(lx0+76,ly0+50,"Fuselage region (not counted)",BLACK,3)
    # row3: actual
    line(lx0+18,ly0+102,lx0+64,ly0+102,RED,2)
    for ox in range(-3,4):
        for oy in range(-3,4):
            if ox*ox+oy*oy<=9: setp(lx0+34+ox,ly0+102+oy,RED)
    text(lx0+76,ly0+90,"Actual span load (CL=%.3f)"%cl_run,BLACK,3)

    # axis names
    text(PL+(PR-PL)//2 - int(6*3*len("Spanwise station, y (m)")/2), PB+46,
         "Spanwise station, y (m)", BLACK, 3)
    text_v(PL-70, PT+(PB-PT)//2 - int(8*3*len("Lift per unit span (kN/m)")/2),
         "Lift per unit span (kN/m)", BLACK, 3)

    # footer
    text(PL, H-40,
         "Elliptic target over loaded span [%.2f,%.2f] m, same total lift (%.0f N) as wing load; dashed = fuselage region, not counted. l0=%.0f N/m." % (ys0, ys1, full_total, L0), DK, 2)

    try:
        write_png(out_file, W, H, img)
    except OSError as e:
        print("ERROR: could not write the PNG (file is locked or folder is read-only).")
        print("-> If elliptical_lift_distribution.png is open in an image viewer /")
        print("   chat preview, close it first, then re-run.")
        print("   Detail:", e)
        sys.exit(1)
    print("Project dir  :", proj)
    print("SPAN=%.4f HSPAN_INNER=%.4f MACH=%s REY=%s"%(SPAN,HSPAN_INNER or -1,MACH,REY))
    print("cl_run=%.4f (AOA=%.4f, Cd=%.4f)  sref=%.2f  total LIFT=%.1f N"%(cl_run,aoa_run,cd_run,sref,lift))
    print("wing loaded span [%.2f, %.2f] m, wing total=%.0f N; target l0=%.1f N/m"%(ys0,ys1,full_total,L0))
    print("fuselage region [0, %.2f] m shown dashed (not counted); YMAX=%d"%(ys0,YMAX))
    print("Wrote", out_file)

if __name__ == "__main__":
    main()
