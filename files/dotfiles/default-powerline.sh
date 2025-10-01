#MT Powerline theme default + colors

#Colors

# Dracula


DCBGDRKDEF="#282a36"
DCBGDRK="#1c1c1c"  #DRK bg
DCBGLDRK="#262626"
DCGRYNTR="#44475a"
DCFGWHT="#f8f8f2"
DCGRYBL="#6272a4"
DCCYDEF="#8be9fd"
DCCYCTR="#87d7ff"
DCGRNDEF="#50fa7b"
DCGRNLT="#87ff87"
DCORDEF="#ffb86c"
DCPKDEF="#ff79c6"
DCPKCR="#ff87d7" #Good drk ctr 
DCPKCTR="#d787d7" #Hostname
DCPRLCTR="#d7afff" # middle light contrast tabs
DCPRDCTR="#af5fd7" #Title
DCPRCTRD2="#af5fff" # Time dark bg contrast
DCPRDEF="#bd93f9"
DCRDDEF="#ff5555"
DCYLDEF="#f1fa8c"

# PaperColor

PCBGGRDRK="#1c1c1c"
PCGRDEF="#808080"
PCGRCTR="#585858"
PCGRMD="#d0d0d0"
PCGBLCTR="#5f8787"
PCSKBLDEF="#5fafd7" #decent blue
PCTLDEF="#00afaf"
PCYLLCTR="#d7af5f"
PCORLCTR="#d7875f"
PCLMLCTR="#afd700"
PCLMDRCTR="#5faf00"
PCGRNDEF="#5faf5f" #gd gre
PCGRNGD="#008700" #Good green
PCPRPDEF="#af87d7"
PCPKDEF="#ff5faf"
PCPKHCTR="#af005f"





# Default Theme

if patched_font_in_use; then
	TMUX_POWERLINE_SEPARATOR_LEFT_BOLD=""
	TMUX_POWERLINE_SEPARATOR_LEFT_THIN=""
	TMUX_POWERLINE_SEPARATOR_RIGHT_BOLD=""
	TMUX_POWERLINE_SEPARATOR_RIGHT_THIN=""
else
	TMUX_POWERLINE_SEPARATOR_LEFT_BOLD="◀"
	TMUX_POWERLINE_SEPARATOR_LEFT_THIN="❮"
	TMUX_POWERLINE_SEPARATOR_RIGHT_BOLD="▶"
	TMUX_POWERLINE_SEPARATOR_RIGHT_THIN="❯"
fi

TMUX_POWERLINE_DEFAULT_BACKGROUND_COLOR=${TMUX_POWERLINE_DEFAULT_BACKGROUND_COLOR:-$DCBGDRK}
TMUX_POWERLINE_DEFAULT_FOREGROUND_COLOR=${TMUX_POWERLINE_DEFAULT_FOREGROUND_COLOR:-$DCPRLCTR}

TMUX_POWERLINE_DEFAULT_LEFTSIDE_SEPARATOR=${TMUX_POWERLINE_DEFAULT_LEFTSIDE_SEPARATOR:-$TMUX_POWERLINE_SEPARATOR_RIGHT_BOLD}
TMUX_POWERLINE_DEFAULT_RIGHTSIDE_SEPARATOR=${TMUX_POWERLINE_DEFAULT_RIGHTSIDE_SEPARATOR:-$TMUX_POWERLINE_SEPARATOR_LEFT_BOLD}

# See man tmux.conf for additional formatting options for the status line.
# The `format regular` and `format inverse` functions are provided as conveinences

if [ -z $TMUX_POWERLINE_WINDOW_STATUS_CURRENT ]; then
	TMUX_POWERLINE_WINDOW_STATUS_CURRENT=(
		"#[$(format inverse)]" \
		"$TMUX_POWERLINE_DEFAULT_LEFTSIDE_SEPARATOR" \
		" #I#F " \
		"$TMUX_POWERLINE_SEPARATOR_RIGHT_THIN" \
		" #W " \
		"#[$(format regular)]" \
		"$TMUX_POWERLINE_DEFAULT_LEFTSIDE_SEPARATOR"
	)
fi

if [ -z $TMUX_POWERLINE_WINDOW_STATUS_STYLE ]; then
	TMUX_POWERLINE_WINDOW_STATUS_STYLE=(
		"$(format regular)"
	)
fi

if [ -z $TMUX_POWERLINE_WINDOW_STATUS_FORMAT ]; then
	TMUX_POWERLINE_WINDOW_STATUS_FORMAT=(
		"#[$(format regular)]" \
		"  #I#{?window_flags,#F, } " \
		"$TMUX_POWERLINE_SEPARATOR_RIGHT_THIN" \
		" #W "
	)
fi

# Format: segment_name background_color foreground_color [non_default_separator]
if [ -z $TMUX_POWERLINE_LEFT_STATUS_SEGMENTS ]; then
	TMUX_POWERLINE_LEFT_STATUS_SEGMENTS=(
		"tmux_session_info $DCPRDCTR $DCBGDRK" \
		"hostname $DCPKCTR $DCBGDRK" \
		#"ifstat 30 255" \
		#"ifstat_sys 30 255" \
		"lan_ip $DCCYCTR $DCBGDRK ${TMUX_POWERLINE_SEPARATOR_RIGHT_THIN}" \
		"wan_ip $DCCYCTR $DCBGDRK" \
		"vcs_branch $DCCYCTR $DCBGDRK" \
		#"vcs_compare 60 255" \
		#"vcs_staged 64 255" \
		#"vcs_modified 9 255" \
		#"vcs_others 245 0" \
	)
fi

if [ -z $TMUX_POWERLINE_RIGHT_STATUS_SEGMENTS ]; then
	TMUX_POWERLINE_RIGHT_STATUS_SEGMENTS=(
		#"earthquake 3 0" \
		"pwd $DCCYCTR $DCBGDRK" \
		#"macos_notification_count 29 255" \
		#"mailcount 9 255" \
		"now_playing $DCBGDRK $DCGRNDEF" \
		#"cpu 240 136" \
		"load $DCBGLDRK $DCPKCR" \
		#"tmux_mem_cpu_load 234 136" \
		"battery $DCBGLDRK $DCGRNLT" \
		#"weather 37 255" \
		#"rainbarf 0 ${TMUX_POWERLINE_DEFAULT_FOREGROUND_COLOR}" \
		#"xkb_layout 125 $DCCYCTR" \
		"date_day $DCBGDRK $DCPRCTRD2" \     # or use 183 for purple value
		"date $DCBGDRK $DCPRCTRD2 ${TMUX_POWERLINE_SEPARATOR_LEFT_THIN}" \
		"time $DCBGDRK $DCPRCTRD2 ${TMUX_POWERLINE_SEPARATOR_LEFT_THIN}" \
		#"utc_time 235 136 ${TMUX_POWERLINE_SEPARATOR_LEFT_THIN}" \
	)
fi