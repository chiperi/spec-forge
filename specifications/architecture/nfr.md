# Non-Functional Requirements — spec-forge (у числах)

> Кожен NFR — вимірюваний і тестований. Для CLI-інструмента (не сервіс) метрики — про детермінізм,
> портованість і якість, а не latency/throughput.

| ID | Атрибут | Ціль (вимірювана) | Як перевіряємо |
|----|---------|-------------------|----------------|
| NFR-001 | Швидкодія (scaffold) | детермінований `init` < 5 с на типовому проєкті | timing test |
| NFR-002 | Портованість | байтово ідентичний вихід на ubuntu/macos/windows | golden test у CI-matrix |
| NFR-003 | Детермінізм | однакові входи → однаковий вихід (без `now()`/random) | golden / repeat test |
| NFR-004 | Надійність | повторний запуск ідемпотентний; блокери зупиняють гейт | unit + e2e |
| NFR-005 | Розширюваність | новий stack-profile / backend без змін ядра | contract test на інтерфейси |
| NFR-006 | Якість коду | Ruff clean; coverage ядра ≥ 85% | quality-gates CI |
| NFR-007 | Безпека | 0 critical vulns; секрети не логуються й не комітяться | SCA + secret-scan |
| NFR-008 | Спостережуваність | structured logs; `--verbose`; зрозумілі exit codes | e2e / manual |

> Звʼязок: NFR-001/002 ← spec NFR-001/002; NFR-002/003 ← SC-005; NFR-005 ← SC-004; NFR-006/007 ← quality gates.
