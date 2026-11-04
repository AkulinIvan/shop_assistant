from app.service import AssistantService


def main() -> None:
    svc = AssistantService()
    print("Ассистент запущен. Введите вопрос ('exit' для выхода):")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit", "выход"):
            break
        if q:
            r = svc.ask(q)
            print(r["answer"])
            print(f"  [source={r['source']}, intent={r['intent']}]")


if __name__ == "__main__":
    main()