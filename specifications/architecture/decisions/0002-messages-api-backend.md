# ADR-0002: Драфтинг через Anthropic Messages API (не Agent SDK)

**Status:** accepted
**Date:** 2026-07-09
**Deciders:** Developer (+ SA)

## Context
FR-010 називає AI-бекенд «Claude Agent SDK». Але реальна операція наповнення
(`draft(persona, context) → text`) — це **single-shot** генерація тексту з системним промптом персони.
Claude Agent SDK / Managed Agents — важча поверхня для агентних циклів з інструментами й контейнерами,
що тут зайва.

## Decision
`ClaudeBackend` реалізовано через **Anthropic Messages API** (`anthropic` SDK,
`client.messages.stream`), модель `claude-opus-4-8`, adaptive thinking, streaming.
Інтерфейс `AIBackend` лишається seam-ом: Agent-SDK / Managed-Agents бекенд можна додати пізніше
без змін ядра.

## Consequences
**Позитивні**
- Простіше, дешевше й доречно для single-shot драфтингу.
- Тестується через `MockBackend` — офлайн, детерміновано, без API-викликів.

**Негативні / компроміси**
- Формальне відхилення від букви FR-010 («Agent SDK») — тому цей ADR. Дух FR-010 (бекенд = Claude,
  через абстракцію) збережено; реальний виклик потребує `ANTHROPIC_API_KEY` або `ant`-профілю.

## Alternatives considered
- **Claude Agent SDK / Managed Agents** — відкинуто для MVP: важче, потребує контейнерів/сесій, не додає
  цінності для single-shot драфтингу. Лишається можливим майбутнім бекендом за тим самим інтерфейсом.
