from src.setup_utils import check_setup


def main():
    if not check_setup():
        return

    from aryas import main
    main()

if __name__ == '__main__':
    main()
