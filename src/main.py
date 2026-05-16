from statistics import median
import sys
import tempfile
from pathlib import Path
from src.core.pipeline import media_to_text

def main() -> None:
    if len(sys.argv) < 2:
        print(f'Usage: python -m src.main <path_to_video>')
        sys.exit(1)

    source = sys.argv[1]
    text = media_to_text(source, model_size='base')
    if '-o' in sys.argv:
        out = Path('/app/output/result.txt')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
        print(f'Saved to {out}')
    else:
        print(text)
if __name__ == '__main__':
    main()