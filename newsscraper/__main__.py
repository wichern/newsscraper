import json
import newsscraper
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 -m newsscraper merge OUT IN[IN*]')
        print('    or python3 -m newsscraper report IN html|csv OUT')
        sys.exit(1)

    if sys.argv[1] == 'merge':
        newsscraper.merge_results(sys.argv[3:], sys.argv[2])
    elif sys.argv[1] == 'report':
        with open(sys.argv[2], 'r', encoding='utf-8') as infile:
            items = json.load(infile)
            with open(sys.argv[4], 'w', encoding='utf-8') as outfile:
                newsscraper.default_report(items, outfile, sys.argv[3])
    else:
        print('Unknown command "{:s}"'.format(sys.argv[1]))
        sys.exit(1)
    sys.exit(0)
