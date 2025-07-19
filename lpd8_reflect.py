import mido, time, math, threading, colorsys
from colorama import init as color_init, Fore, Style

# Initialize colorama
color_init(autoreset=True)

# === CONFIG ===
IN_PORT_IDX       = None  # set to None to pick at runtime
OUT_PORT_IDX      = None

# Breathing pad groups
BREATH_GROUP1     = {0,1}    # pads 1,2: red→yellow
BREATH_GROUP2     = {4,5}    # pads 5,6: light green→dark blue

# Static pad groups
STATIC_BLUE_PADS   = {2,3}   # pads 3,4: light blue
STATIC_ORANGE_PADS = {6,7}   # pads 7,8: orange

# Ripple-enabled pads
RIPPLE_PADS        = BREATH_GROUP1.union(BREATH_GROUP2)

# Timing settings
BREATH_PERIOD     = 2.0      # seconds full breathing cycle
BG_INTERVAL       = 0.05     # seconds between background updates

# Ripple settings
RIPPLE_DURATION   = 0.1      # total seconds for ripple animation
MAX_RIPPLE_RADIUS = 2        # how many pads outward
RIPPLE_INTERVAL   = RIPPLE_DURATION / (MAX_RIPPLE_RADIUS + 1)

# Initialization animation settings
INIT_DURATION     = 5.0      # seconds for startup animation
INIT_INTERVAL     = 0.05     # seconds between init frames

# Color definitions
LIGHT_BLUE   = (0,127,127)
ORANGE       = (127,63,0)
LIGHT_GREEN  = (0,127,0)
YELLOW       = (127,127,0)
RED          = (127,0,0)
WHITE_SYSEX  = (127,127,127)

# Helpers
def pack7(v): return [v>>7, v&0x7F]

def build_pad_sysex(pad_colors):
    """Build SysEx data bytes (no F0/F7) for 8-pad RGB colors."""
    syx = [0xF0,0x47,0x7F,0x4C,0x06,0x00,0x30]
    for r,g,b in pad_colors:
        syx += pack7(r) + pack7(g) + pack7(b)
    syx.append(0xF7)
    return syx[1:-1]

# Ripple gradient (white)
GRADIENT = {0: WHITE_SYSEX, 1: WHITE_SYSEX, 2: WHITE_SYSEX}

# Runtime state and controls
pad_state = [False]*8
pause_bg  = threading.Event()
stop_bg   = threading.Event()

# Background thread: breathing/static effect
def background_loop(outport):
    start = time.time()
    while not stop_bg.is_set():
        if not pause_bg.is_set():
            t = (time.time() - start) % BREATH_PERIOD
            phase = 2*math.pi*t / BREATH_PERIOD
            v = int((math.sin(phase - math.pi/2) + 1)/2 * 127)
            colors = []
            for i in range(8):
                if pad_state[i]:
                    if i in BREATH_GROUP1:
                        colors.append((127, v, 0))       # red→yellow
                    elif i in BREATH_GROUP2:
                        colors.append((0, 127-v, v))     # green→blue
                    elif i in STATIC_BLUE_PADS:
                        colors.append(LIGHT_BLUE)
                    elif i in STATIC_ORANGE_PADS:
                        colors.append(ORANGE)
                    else:
                        colors.append((0,0,0))
                else:
                    colors.append((0,0,0))
            outport.send(mido.Message('sysex', data=build_pad_sysex(colors)))
        time.sleep(BG_INTERVAL)

# Ripple animation on pad press
def animate_ripple(idx, outport):
    """White ripple outward over RIPPLE_DURATION seconds."""
    frame = [(0,0,0)]*8
    frame[idx] = GRADIENT[0]
    outport.send(mido.Message('sysex', data=build_pad_sysex(frame)))
    time.sleep(RIPPLE_INTERVAL)
    for d in range(1, MAX_RIPPLE_RADIUS+1):
        frame = [(0,0,0)]*8
        frame[idx] = GRADIENT[0]
        if idx-d >= 0: frame[idx-d] = GRADIENT[d]
        if idx+d < 8:  frame[idx+d] = GRADIENT[d]
        outport.send(mido.Message('sysex', data=build_pad_sysex(frame)))
        time.sleep(RIPPLE_INTERVAL)

# Initialization animation: morph hues over INIT_DURATION, abort on input, ends white
def init_animation(inport, outport):
    base_hues = [i/8.0 for i in range(8)]
    steps = int(INIT_DURATION / INIT_INTERVAL)
    for step in range(steps):
        for msg in inport.iter_pending():
            if msg.type in ('note_on','note_off','control_change'):
                return
        t = step / steps
        pad_colors = []
        for i, base in enumerate(base_hues):
            hue = (base + t) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            pad_colors.append((int(r*127), int(g*127), int(b*127)))
        outport.send(mido.Message('sysex', data=build_pad_sysex(pad_colors)))
        time.sleep(INIT_INTERVAL)
    white_frame = [(127,127,127)]*8
    outport.send(mido.Message('sysex', data=build_pad_sysex(white_frame)))
    time.sleep(0.2)

# Utility to list available ports with color
def list_ports(title, ports):
    print(Fore.CYAN + title)
    for i, name in enumerate(ports):
        print(Fore.YELLOW + f"  {i}: {name}")
    print(Style.RESET_ALL, end='')

# Main execution
def main():
    # Fetch port lists
    in_ports  = mido.get_input_names()
    out_ports = mido.get_output_names()

    # Display menus
    list_ports("MIDI INPUTS:",  in_ports)
    list_ports("MIDI OUTPUTS:", out_ports)

    # Prompt user
    in_idx  = IN_PORT_IDX  if IN_PORT_IDX is not None else int(input(Fore.GREEN + "Select INPUT port #: " + Style.RESET_ALL))
    out_idx = OUT_PORT_IDX if OUT_PORT_IDX is not None else int(input(Fore.GREEN + "Select OUTPUT port #: " + Style.RESET_ALL))

    # Opening ports info
    print(Fore.MAGENTA + f"\nOpening IN  → {in_ports[in_idx]}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"Opening OUT → {out_ports[out_idx]}\n" + Style.RESET_ALL)

    with mido.open_input(in_ports[in_idx]) as inport, mido.open_output(out_ports[out_idx]) as outport:
        print(Fore.WHITE + Style.BRIGHT + "Hello World\n" + Style.RESET_ALL)
        init_animation(inport, outport)

        bg = threading.Thread(target=background_loop, args=(outport,), daemon=True)
        bg.start()

        print(Fore.WHITE + "Listening for pads 1–8 (notes 36–43)…" + Fore.CYAN + " Press Ctrl+C to quit.\n" + Style.RESET_ALL)
        try:
            while True:
                for msg in inport.iter_pending():
                    if msg.type in ('note_on','note_off') and 36 <= msg.note <= 43:
                        idx = msg.note - 36
                        status = "ON" if msg.type=='note_on' and msg.velocity>0 else "OFF"
                        color = Fore.GREEN if status=="ON" else Fore.RED
                        print(color + f"⟵ {msg} -> Pad {idx+1} {status}" + Style.RESET_ALL)
                        pad_state[idx] = (status=="ON")
                        pause_bg.set()
                        if idx in RIPPLE_PADS and status=="ON":
                            animate_ripple(idx, outport)
                        pause_bg.clear()
                time.sleep(0.01)
        except KeyboardInterrupt:
            print(Fore.RED + "\nShutting down… clearing LEDs and closing ports..." + Style.RESET_ALL)
            stop_bg.set()
            off_frame = [(0,0,0)]*8
            outport.send(mido.Message('sysex', data=build_pad_sysex(off_frame)))
            time.sleep(0.1)
    print(Fore.GREEN + "Exited cleanly." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
