
import subprocess
from libqtile import bar, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

# theme.

#     border = {
#         'border_focus':Green.light2,
#         "border_normal":Green.dark1,
#         "border_width":2,
#         'single_border_width':0
#     }


terminal = guess_terminal()
filemanager = f"{terminal} -e nnn"
appfider = ""
telegram = "telegram-desktop"
browser = "google-chrome-stable"
goland = ""
screenshoter = ""
capturerect = ""
taskmanager = f"{terminal} -e btop"
clipboard = ""
codeeditor = "code"

ALT = "mod1"
SUPER = "mod4"
CTRL = "control"
SHIFT = "shift"
ESC = "Escape"
LEFT_CLICK = "Button1"
MIDDLE_CLICK = "Button2"
RIGHT_CLICK = "Button3"

keys = [
    # Run applications
    Key([SUPER], "t", lazy.spawn(terminal), desc="Launch terminal"),
    Key([SUPER], "w", lazy.spawn(browser), desc="Launch browser"),
    Key([SUPER], "g", lazy.spawn(telegram), desc="Launch telegram"),
    Key([SUPER], "e", lazy.spawn(filemanager), desc="Launch filemanager"),
    Key([SUPER], "a", lazy.spawn(codeeditor), desc="Launch codeeditor"),
    Key([CTRL, SHIFT], ESC, lazy.spawn(taskmanager), desc="Launch taskmanager"),
    Key([SUPER], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"), # instead appfinder

    # Switch between windows
    Key([SUPER], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([SUPER], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([SUPER], "j", lazy.layout.down(), desc="Move focus down"),
    Key([SUPER], "k", lazy.layout.up(), desc="Move focus up"),

    # Move column's window
    Key([SUPER, SHIFT], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([SUPER, SHIFT], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([SUPER, SHIFT], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([SUPER, SHIFT], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Resize column's window
    Key([SUPER, CTRL], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([SUPER, CTRL], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([SUPER, CTRL], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([SUPER, CTRL], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([SUPER], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    #
    Key([SUPER], "c", lazy.window.kill(), desc="Kill focused window"),
    Key([SUPER], "m", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([SUPER], "f", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),


    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [SUPER, SHIFT],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    # Toggle between different layouts as defined below
    Key([SUPER], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key(
        [SUPER],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([SUPER, CTRL], "r", lazy.reload_config(), desc="Reload the config"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            [CTRL, ALT],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [SUPER],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [SUPER, SHIFT],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, SHIFT], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

# layouts
layout_theme = {
    "margin": 7,
    "border_focus": "#0663e8dd",
    "border_normal": "#595959aa",
    "border_on_single": False,
    "border_width": 2,
}

layouts = [
    layout.Columns(**layout_theme),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
    foreground="#bab0af"
)
extension_defaults = widget_defaults.copy()


# Indicator of "us,ru - layouts + grp_led:caps" fnality
class KeyboardLayoutCapsIndicator(widget.CapsNumLockIndicator):
    shCmd = "setxkbmap -query | grep layout | awk '{print $2}'"
    layouts = subprocess.check_output(shCmd, shell=True, text=True).strip().split(',')
    last = None
    def poll(self):
        # [('Caps', 'off'), ('Num', 'off')]
        capsOn = self.get_indicators()[0][1] == 'on' 
        val = self.layouts[1] if capsOn else self.layouts[0]
        if self.last and val != self.last:
            subprocess.run([f"notify-send {val.upper()}"], shell=True)
        self.last = val
        return val


screens = [
    Screen(
        top=bar.Bar(
            [
                KeyboardLayoutCapsIndicator(foreground="#ffffff"),
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
                widget.Systray(),
                widget.clock.Clock(format="%H:%M"),
                widget.Battery(
                    foreground="#C2CFA1",
                    format="{char}{percent:2.0%} {watt:.2f}W",
                ),
                widget.Memory(
                    foreground="#87B9F3",
                    format="{MemUsed: .0f}{mm}",
                    measure_mem="G",
                    update_interval=5,
                ),
                widget.QuickExit(
                    default_text="[ die ]",
                    countdown_format="[ {} ]"
                ),
            ],
            24,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
]

# Drag floating layouts.
mouse = [
    Drag([SUPER], LEFT_CLICK, lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([SUPER], RIGHT_CLICK, lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([SUPER], MIDDLE_CLICK, lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = True
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
