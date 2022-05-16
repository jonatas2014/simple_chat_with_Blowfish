for counter in $(seq 1 1200); do
  echo "counter: $counter"
  python3 client.py "127.0.1.1" 5050
done