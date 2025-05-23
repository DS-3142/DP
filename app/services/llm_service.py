import google.generativeai as genai
genai.configure(api_key="AIzaSyAY3DtZzT-9yIJtoIwMP3_iFhGmNN6TlY0")
from typing import List
from app.dtos.crawled_paper_dto import CrawledPaper
from app.dtos.keyword_summary_dto import KeywordSummaryResult
from app.dtos.summarized_paper_dto import SummarizedPaper


def extract_keywords(text: str) -> KeywordSummaryResult:
    """
    회의록 텍스트로부터 키워드와 요약을 추출 (Gemini API 활용)
    """
    meeting_prompt = f"""
    The following is a meeting transcript from a research lab.
    Please extract 5 core research keywords in English, each keyword should be 1-3 words, and output as a list.

    [Meeting Transcript]
    ---
    {text}
    ---
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(meeting_prompt)
    # Gemini 응답에서 키워드 리스트 추출 (예: ['키워드1', '키워드2', ...])
    keywords = []
    for line in response.text.strip().splitlines():
        kw = line.strip("-•* ")
        if kw:
            keywords.append(kw)
    keywords = keywords[:5]
    summary_prompt = f"""
    다음은 한 연구실의 회의록입니다.
    이 회의록의 주요 논의 내용을 2~3문장으로 자연스럽게 요약해 주세요.

    [회의록 입력]
    ---
    {text}
    ---
    """
    summary_response = model.generate_content(summary_prompt)
    summary = summary_response.text.strip()

    return KeywordSummaryResult(
        summary=summary,
        keywords=keywords
    )

def summarize_papers(papers: List[CrawledPaper]) -> List[SummarizedPaper]:
    """
    크롤링된 논문 리스트에 대해 요약을 추가한 SummarizedPaper 리스트 반환 (Gemini API 활용)
    """
    results = []
    model = genai.GenerativeModel("gemini-1.5-flash")
    for paper in papers:
        text = paper.text_content
        if not text or "error" in text.lower() or "no usable" in text.lower():
            summary = "요약 불가: 본문 크롤링 실패"
        else:
            paper_prompt = f"""
            다음 논문의 핵심 내용을 4~5문장 이내로 요약해 주세요.  
            논문이 해결하고자 한 문제, 제안한 방법, 실험 결과를 중심으로 간결하게 서술해 주세요.

            [논문 초록]
            ---
            {text}
            ---
            """
            response = model.generate_content(paper_prompt)
            summary = response.text.strip()
            results.append(SummarizedPaper(
            paper_id=paper.paper_id,
            title=paper.title,
            thesis_url=paper.thesis_url,
            text_content=paper.text_content,
            summary=summary
        ))
    return results