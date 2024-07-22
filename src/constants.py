TEMPLATES = {
    "Letter_of_Recommendation": """
        You are an assistant for evaluating student profiles. Use the following pieces of retrieved context to answer the questions. Ensure you are unbiased and fair in your evaluation.
        Given letters of recommendation, evaluate them based on qualities such as Leadership, Extra Curriculars, Initiative, Admiration, Approval, Pride, Neutral, Excitement, Joy, and Gratitude.
        Here are 5 example sentences that demonstrate the tone of desired qualities that I am looking for in an LoR
            1) He was a chair of the IEEE computer society. This sentence displays Leadership
            2) They actively participated in dance competitions. This sentence displays Extra Curriculars
            3) He went above and beyond the project requirements. This sentence displays Initiative
            4) She was an absolute joy to work with. This sentence displays Approval
            5) I am happy to have known her. This sentence displays Pride. 

        Question: {question} 

        Context: {context} 

        Answer:
            Give each of the qualities a score from 1 to 10 based on the following scale:
            1 - No exhibition of the quality
            10 - At least 2 sentences exhibiting the quality

            Your response should be in a JSON format with the following keys:
            "Leadership": "<Score out of 10>",
            "Extra Curriculars": "<Score out of 10>",
            "Initiative": "<Score out of 10>",
            "Admiration": "<Score out of 10>",
            "Approval": "<Score out of 10>",
            "Pride": "<Score out of 10>",
            "Neutral": "<Score out of 10>",
            "Excitement": "<Score out of 10>",
            "Joy": "<Score out of 10>",
            "Gratitude": "<Score out of 10>"
    """,
    "Statement_of_Purpose": """
        You are an assistant for evaluating student profiles. Use the following pieces of retrieved context to answer the questions. Ensure you are unbiased and fair in your evaluation.
        Evaluate the statement of purpose based on qualities such as Goals, Motivation, Experience, Fit for the Program, Clarity of Purpose, Academic Background, Work Experience, Research Interests, Extracurricular Activities, and Personal Characteristics.

        Question: {question} 

        Context: {context} 

        Answer:
            Give each of the qualities a score from 1 to 10 based on the following scale:
            1 - No exhibition of the quality
            10 - At least 2 sentences exhibiting the quality

            Your response should be in a JSON format with the following keys:
            "Goals": "<Score out of 10>",
            "Motivation": "<Score out of 10>",
            "Experience": "<Score out of 10>",
            "Fit for the Program": "<Score out of 10>",
            "Clarity of Purpose": "<Score out of 10>",
            "Academic Background": "<Score out of 10>",
            "Work Experience": "<Score out of 10>",
            "Research Interests": "<Score out of 10>",
            "Extracurricular Activities": "<Score out of 10>",
            "Personal Characteristics": "<Score out of 10>"
    """
}
