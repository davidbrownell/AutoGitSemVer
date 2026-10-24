# Sourced by the release steps so that transient network failures do not fail a release. Only pass
# commands that are safe to repeat.
retry() {
  local attempt

  for attempt in 1 2 3; do
    if "$@"; then
      return 0
    fi

    if [ "${attempt}" -lt 3 ]; then
      echo "Attempt ${attempt} of '$*' failed; retrying in 15 seconds." >&2
      sleep 15
    fi
  done

  return 1
}
