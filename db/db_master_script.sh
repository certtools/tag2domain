SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIR"

for dir in $(find $(pwd) -mindepth 1 -maxdepth 1 -type d | sort); do
    echo "Running scripts in directory $dir"
    for script in $(find $dir -name "*.sh" -type f); do
        echo "-- running script $script"
        bash $script
    done
done
