per_speaker_codec() {
	for candidate in /sys/devices/platform/soc/*.i2c/i2c-*/?-????; do
		while IFS= read -r -d '' compatible ; do
			case "$compatible" in
				ti,tas5770|ti,sn012776)
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

print_die_temp() {
	echo "$2:" $(cat $1/die_temp)
}

per_speaker_codec print_die_temp
