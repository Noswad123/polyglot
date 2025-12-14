import argparse
from .actions.trackables import list_items, show_status, update_progress
from .actions.kata import handle_kata
from .actions.concepts import show_concept
from .actions.yaml_ingest import ingest_all
from .actions.yaml_export import export_all

def build_parser() -> argparse.ArgumentParser:
    valid_choices = ["list", "show", "run", "status", "progress", "kata", "yaml-ingest", "yaml-export"]
    parser = argparse.ArgumentParser(prog="pylearn")
    parser.add_argument("command", choices=valid_choices, help="Command to execute")

    parser.add_argument("--type")      # for list/status/progress
    parser.add_argument("--name")      # concept/kata/project name
    parser.add_argument("--language")  # optional language filter
    parser.add_argument("--update")    # progress update target name (or use --name)
    parser.add_argument("--status")    # new status for progress
    parser.add_argument("--file", action="store_true")
    parser.add_argument("--answer", action="store_true")
    parser.add_argument("--edit", action="store_true")
    parser.add_argument("--dojo", action="store_true")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    match args.command:
        case "list":
            if not args.type:
                print("❌ --type is required for 'list' (language|concept|kata|project).")
            else:
                list_items(args.type)

        case "show":
            if not args.name:
                print("❌ --name (concept name) is required for 'show'.")
            else:
                show_concept(args.name, args.language)

        case "run":
            # hook for future "run script/project"
            print("not implemented")

        case "status":
            show_status(args.type)

        case "progress":
            target_name = args.update or args.name
            if not (target_name and args.type and args.status):
                print("❌ progress requires --type, --status, and --update or --name.")
            else:
                update_progress(target_name, args.type, args.status)

        case "kata":
            if not (args.name and args.language) and not args.dojo:
                print("❌ kata requires --name and --language.")
            else:
                handle_kata(
                    args.name,
                    args.language,
                    args.file,
                    args.answer,
                    args.edit,
                    args.dojo
                )
        case "yaml-ingest":#️⃣
            ingest_all()
        case "yaml-export":#️⃣
            export_all(zip_after=False)

if __name__ == "__main__":
    main()
