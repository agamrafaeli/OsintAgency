#!/usr/bin/env python3
"""Demonstrate the legacy quran_detector API on mixed sample strings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import shorten
from typing import Protocol, Sequence

from osintagency.services import quran_detector


@dataclass(frozen=True)
class SampleInput:
    """Input fixture describing what text to scan."""

    label: str
    text: str
    contains_verse: bool


class DetectorInterface(Protocol):
    """Public contract we expect from quran_detector."""

    def match_all(self, text: str) -> list[dict]:
        """Return structured match dicts for a chunk of text."""


class QuranDetectorAdapter:
    """Adapter that exposes qMatcherAnnotater via the DetectorInterface contract."""

    def __init__(self, detector: quran_detector.qMatcherAnnotater):
        self._detector = detector

    def match_all(self, text: str) -> list[dict]:
        return self._detector.matchAll(text)


@dataclass(frozen=True)
class TableRow:
    """Renderable row destined for stdout."""

    sample_index: int
    sample_label: str
    expected_contains_verse: bool
    match_index: int | None
    detected_span: str
    snippet: str
    match_keys: str


class SampleResultMapper:
    """Translate detector records into printable table rows."""

    def __init__(self, snippet_width: int = 48):
        self.snippet_width = snippet_width

    @staticmethod
    def _summarize_matches(matches: list[dict]) -> str:
        if not matches:
            return "—"
        spans = []
        for match in matches:
            start = match["aya_start"]
            end = match["aya_end"]
            if start == end:
                span = f"{match['aya_name']}:{start}"
            else:
                span = f"{match['aya_name']}:{start}-{end}"
            spans.append(span)
        return "; ".join(spans)

    def build_rows(self, index: int, sample: SampleInput, matches: list[dict]) -> list[TableRow]:
        snippet = shorten(sample.text, width=self.snippet_width, placeholder="…")
        if not matches:
            return [
                TableRow(
                    sample_index=index,
                    sample_label=sample.label,
                    expected_contains_verse=sample.contains_verse,
                    match_index=None,
                    detected_span="—",
                    snippet=snippet,
                    match_keys="",
                )
            ]

        rows: list[TableRow] = []
        for match_idx, match in enumerate(matches, start=1):
            rows.append(
                TableRow(
                    sample_index=index,
                    sample_label=sample.label,
                    expected_contains_verse=sample.contains_verse,
                    match_index=match_idx,
                    detected_span=self._summarize_matches([match]),
                    snippet=snippet,
                    match_keys=", ".join(match.keys()),
                )
            )
        return rows


class TablePrinter:
    """Presentation logic for report rows."""

    headers = ("Sample #", "label", "contains verse", "match #", "detected aya", "input snippet", "JSON keys")

    def render(self, rows: Sequence[TableRow]) -> None:
        normalized_rows = [
            (
                row.sample_index,
                row.sample_label,
                "yes" if row.expected_contains_verse else "no",
                row.match_index if row.match_index is not None else "-",
                row.detected_span,
                row.snippet,
                row.match_keys,
            )
            for row in rows
        ]

        col_widths = [len(header) for header in self.headers]
        for row in normalized_rows:
            for idx, cell in enumerate(row):
                col_widths[idx] = max(col_widths[idx], len(str(cell)))

        def format_row(row: tuple) -> str:
            return " | ".join(str(cell).ljust(col_widths[idx]) for idx, cell in enumerate(row))

        divider = "-+-".join("-" * width for width in col_widths)
        print(format_row(self.headers))
        print(divider)
        for row in normalized_rows:
            print(format_row(row))


def build_report_rows(
    detector: DetectorInterface,
    samples: Sequence[SampleInput],
    mapper: SampleResultMapper,
) -> list[TableRow]:
    rows: list[TableRow] = []
    for idx, sample in enumerate(samples, start=1):
        matches = detector.match_all(sample.text)
        rows.extend(mapper.build_rows(idx, sample, matches))
    return rows


SAMPLES: Sequence[SampleInput] = (
    SampleInput(
        label="Verse 1",
        text="الحمد لله رب العالمين الرحمن الرحيم مالك يوم الدين",
        contains_verse=True,
    ),
    SampleInput(
        label="Verse 2",
        text="قل هو الله احد الله الصمد لم يلد ولم يولد ولم يكن له كفوا احد",
        contains_verse=True,
    ),
    SampleInput(
        label="Verse 3",
        text="الله لا اله الا هو الحي القيوم لا تاخذه سنة ولا نوم",
        contains_verse=True,
    ),
    SampleInput(
        label="Verse 4",
        text="يا ايها الذين امنوا اتقوا الله وكونوا مع الصادقين",
        contains_verse=True,
    ),
    SampleInput(
        label="Verse 5",
        text="ربنا اتنا في الدنيا حسنة وفي الاخرة حسنة وقنا عذاب النار",
        contains_verse=True,
    ),
    SampleInput(
        label="Plain 1",
        text="The quick brown fox jumps over the lazy dog.",
        contains_verse=False,
    ),
    SampleInput(
        label="Plain 2",
        text="Data pipelines should log every failure before retries.",
        contains_verse=False,
    ),
    SampleInput(
        label="Plain 3",
        text="We meet at noon to plan the product release roadmap.",
        contains_verse=False,
    ),
    SampleInput(
        label="Plain 4",
        text="Rain showers turned into a brilliant double rainbow.",
        contains_verse=False,
    ),
    SampleInput(
        label="Plain 5",
        text="This sentence intentionally avoids any scripture content.",
        contains_verse=False,
    ),
)


def ensure_data_files_exist(repo_root: Path) -> None:
    data_dir = repo_root / "dfiles"
    if not data_dir.exists():
        raise SystemExit(
            f"Expected Quran data files under {data_dir}. "
            "Place quran-index.xml, quran-simple.txt, and nonTerminals.txt there."
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    ensure_data_files_exist(repo_root)

    detector = QuranDetectorAdapter(quran_detector.qMatcherAnnotater())
    mapper = SampleResultMapper()
    rows = build_report_rows(detector, SAMPLES, mapper)
    TablePrinter().render(rows)


if __name__ == "__main__":
    main()
