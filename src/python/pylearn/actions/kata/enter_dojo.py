from ...config import KATAS_DIR
from .common import build_initial_buffer, fetch_previous_solution, run_kata_once

def _choose_kata() -> str | None:
    katas = sorted(
        [p.stem for p in KATAS_DIR.glob("*.md") if p.name not in {"index.md"}],
        key=str.lower,
    )

    if not katas:
        print("❌ No katas found in KATAS_DIR.")
        return None

    print("🧵 Available katas:")
    for idx, name in enumerate(katas, start=1):
        print(f"  {idx}. {name}")
    print("  q. quit")

    while True:
        choice = input("\nChoose a kata (number or name, 'q' to quit): ").strip()
        if choice.lower() in {"q", "quit"}:
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(katas):
                return katas[idx - 1]
            print("⚠️ Invalid index. Try again.")
            continue

        if choice in katas:
            return choice

        print("⚠️ Not a valid kata. Try again.")


def _choose_language() -> str | None:
    languages = ["python"]

    print("\n🗣  Available languages:")
    for idx, lang in enumerate(languages, start=1):
        print(f"  {idx}. {lang}")
    print("  q. quit")

    while True:
        choice = input("\nChoose a language (number or name, 'q' to quit): ").strip()
        if choice.lower() in {"q", "quit"}:
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(languages):
                return languages[idx - 1]
            print("⚠️ Invalid index. Try again.")
            continue

        lowered = choice.lower()
        for lang in languages:
            if lang.lower() == lowered:
                return lang

        print("⚠️ Not a valid language. Try again.")


def enter_dojo() -> None:
    """
    Interactive kata loop:

    - pick a kata
    - pick a language
    - reuse the same buffer + test workflow as handle_kata
    - on failure: re-edit, inspect previous solution, or quit
    """

    print("🥋 Welcome to the dojo!\n")

    kata_name = _choose_kata()
    if kata_name is None:
        print("👋 Leaving the dojo.")
        return

    language = _choose_language()
    if language is None:
        print("👋 Leaving the dojo.")
        return

    language = language.lower()
    print(f"\n🥊 Entering kata '{kata_name}' in {language}...\n")

    # Start with a fresh buffer
    current_buffer = build_initial_buffer(
        kata_name=kata_name,
        language=language,
        existing_code=None,
    )

    while True:
        success, current_buffer = run_kata_once(
            kata_name=kata_name,
            language=language,
            initial_buffer=current_buffer,
        )

        if success:
            while True:
                action = (
                    input("\nOptions: [s]ee previous solution, [q]uit dojo: ")
                    .strip()
                    .lower()
                )
                if not action or action.startswith("q"):
                    print("🎉 Well done. Leaving the dojo.")
                    return
                if action.startswith("s"):
                    prev = fetch_previous_solution(kata_name, language)
                    if prev:
                        print("\nPrevious solution:\n" + "-" * 40)
                        print(prev)
                        print("-" * 40)
                    else:
                        print("ℹ️ No previous successful solution stored yet.")
                else:
                    print("⚠️ Unknown option. Try again.")
        else:
            print("❌ Tests failed.")
            while True:
                action = (
                    input(
                        "\nOptions: [e]dit again, [s]ee previous solution, [q]uit dojo: "
                    )
                    .strip()
                    .lower()
                )
                if not action or action.startswith("e"):
                    # Reuse current_buffer (the failing attempt) for the next edit
                    break
                if action.startswith("s"):
                    prev = fetch_previous_solution(kata_name, language)
                    if prev:
                        print("\nPrevious solution:\n" + "-" * 40)
                        print(prev)
                        print("-" * 40)
                    else:
                        print("ℹ️ No previous successful solution found.\n")
                elif action.startswith("q"):
                    print("👋 Leaving the dojo. Come back soon.")
                    return
                else:
                    print("⚠️ Unknown option. Try again.")
