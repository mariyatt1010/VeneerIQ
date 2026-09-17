from llm_utils import client, MODEL_NAME


def generate_business_summary(user_question, result_df):
    """
    Sends the question + the ACTUAL returned data to Gemini and asks for a
    short, grounded business insight. The AI is explicitly instructed to
    use only the data provided and never invent numbers or facts.
    """
    if result_df is None or result_df.empty:
        return "No data was returned for this question."

    # Limit rows sent to the AI - keeps the prompt small and avoids noise
    sample_df = result_df.head(15)
    data_text = sample_df.to_string(index=False)

    prompt = f"""
You are a business analyst. Below is the exact data returned for a user's question.

Question: "{user_question}"

Data:
{data_text}

Instructions:
- Write a concise 1-2 sentence business insight based ONLY on this data.
- Do NOT invent any numbers, names, or facts that are not shown above.
- If the data shown is only a partial sample of a larger result, do not claim it is the complete picture.
- Write in plain, professional business language. No SQL, no code, no markdown.

Summary:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()