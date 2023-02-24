#!/bin/sh
set -e

get_driver() {
	while IFS= read -r -d '' compatible ; do
		case "$compatible" in
			ti,tas5770l)
				driver="/sys/bus/i2c/drivers/tas2770"
				;;
			ti,sn012776)
				driver="/sys/bus/i2c/drivers/tas2764"
				;;
			cirrus,cs42l83)
				driver="/sys/bus/i2c/drivers/cs42l83"
				;;
			cirrus,cs42l84)
				driver="/sys/bus/i2c/drivers/cs42l84"
				;;
		esac
	done < $candidate/of_node/compatible
}

per_speaker_codec() {
	for candidate in /sys/devices/platform/soc/*.i2c/i2c-*/?-????; do
		while IFS= read -r -d '' compatible ; do
			case "$compatible" in
				ti,tas5770l|ti,sn012776|cirrus,cs42l83|cirrus,cs42l84)
					if test -f "$candidate/of_node/sound-name-prefix"; then
						IFS= read -r -d '' name \
							< $candidate/of_node/sound-name-prefix
					else
						name="Speaker"
					fi
					$1 "$candidate" "$name"
					;;
			esac
		done < $candidate/of_node/compatible
	done
}

unbind() {
	echo "Unbinding $2..."
	name=`basename $1`
	if test -d "$1/driver"; then
		echo "$name" > "$1/driver/unbind"
	fi
}

bind() {
	echo "Binding $2..."
	name=`basename $1`
	get_driver "$1"
	echo "$name" > "$driver/bind"
}

per_speaker_codec unbind
per_speaker_codec bind
