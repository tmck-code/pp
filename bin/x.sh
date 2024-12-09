#!/bin/bash

[ "${DEBUG:-}" == true ] && set -euxo pipefail

usage() {
    echo "palette-to-rgb [COL] [-rgb] [-raw] [-C] [-h]"
    echo "Show RGB values of the standard terminal 256-color palette."
    echo "If COL is given (number 0-255), show only the given color."
    echo "Options:"
    echo "  -rgb  Format as \"rgb(R, G, B)\" instead of \"#RRGGBB\""
    echo "  -raw  Show the value only"
    echo "  -C    Force coloring even when piped"
    echo "  -pastel    Use 'pastel' to show more colour info"
}

std_colors=(
    0   0   0    #  0 black
    128 0   0    #  1 red
    0   128 0    #  2 green
    128 128 0    #  3 yellow
    0   0   128  #  4 blue
    128 0   128  #  5 magenta
    0   128 128  #  6 cyan
    192 192 192  #  7 white (light grey)
    128 128 128  #  8 grey
    255 0   0    #  9 bright red
    255 255 0    # 10 bright green
    0   255 0    # 11 bright yellow
    0   0   255  # 12 bright blue
    255 0   255  # 13 bright magenta
    0   255 255  # 14 bright cyan
    255 255 255  # 15 bright white
)

test -x /opt/homebrew/bin/gecho && echo=gecho || echo=echo

echo_msg() {
  $echo "${@}"
}

# 6x6x6 cube color component
cube_component() {
    local i=$(( (($1 - 16) / $2) % 6 ))
    # >&2 gecho -n "(\$1=$1, \$2=$2, i=$i) "
    (( $i == 0 )) && echo_msg 0 || echo_msg $(( ( 14135 + 10280 * $i ) / 256 ))
}

get_color() {
    local r g b fmt
    if (( $1 < 16 )); then
        r=${std_colors[$(( $1 * 3 + 0 ))]}
        g=${std_colors[$(( $1 * 3 + 1 ))]}
        b=${std_colors[$(( $1 * 3 + 2 ))]}
    elif (( $1 < 232 )); then # < 6*6*6+16 ?
        # colors 16-231 (6x6x6 cube):
        r=$(cube_component $1 36)
        g=$(cube_component $1 6)
        b=$(cube_component $1 1)
    else
        # colors 232-255 (grayscale):
        r=$(( ( 2056 + 2570 * ($1 - 232) ) / 256 ))
        g=$r
        b=$r
    fi
    # >&2 echo
    [[ -n $rgb ]] && fmt='rgb(%3i, %3i, %3i)' || fmt='#%02x%02x%02x'
    printf "$fmt" $r $g $b
}

print_color() {
    local pastel=$2
    if [[ -n $raw ]]; then
        get_color $1
    else
        printf '%03i: %-19s' $1 "$(get_color $1): "
        # Show a colored box if not piped (or with option -C )
        if [[ -t 1 || -n $colored ]]; then
          s="        "
          echo_msg -en "\e[48;5;${1}m$s\e[0m "
        fi
        echo
    fi
    rgb=$(get_color $1)
    [[ -n $pastel ]] && pastel color "$rgb"
}

color= colored= rgb= raw= pastel=
for arg in "$@"; do
    if [[ $arg == -h ]]; then usage; exit
    elif [[ $arg =~ ^[0-9]+$ ]]; then
        (( $arg > 255 )) && { echo_msg "Wrong color code" >&2; exit 1; }
        color=$arg
    elif [[ $arg == -C ]]; then colored=1
    elif [[ $arg == -rgb ]]; then rgb=1
    elif [[ $arg == -raw ]]; then raw=1
    elif [[ $arg == -pastel ]]; then pastel=1
    else echo_msg "Wrong arg: $arg" >&2; exit 1
    fi
done

if [[ -n $color ]]; then
    print_color $color $pastel
else
    for n in {0..255}; do
        print_color $n $pastel
    done
fi
