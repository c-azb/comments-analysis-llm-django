
from transformers import pipeline
import emoji
import unicodedata

class SentimentClassifier:
    def __init__(self):
        self.pipe = None
    
    def clean_comments(self,x): #conver emoji to text and conver others to ascii
        x = emoji.demojize(x).replace('♡',' heart ')
        x = re.sub(r'[\_\-\:]',' ',x)
        x = unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode('utf-8','ignore')
        return re.sub(r'\s+',' ',x).lower().strip()

    def process_comments(self,comments,separator):
        comments = comments.split(separator)
        results = self.process_pipe(comments)

        overall_sent = OverallSent()
        overall_sent.add_sentences(comments,results)
        return overall_sent

    def process_pipe(self,x):
        x = [self.clean_comments(comment) for comment in x ]
        if self.pipe is None:
            self.pipe = pipeline('text-classification','ft-classifier')
        return self.pipe(x)

class OverallSent:
    def __init__(self):
        self.sentences = []
        self.sent_count = {'Positive': 0,'Negative': 0,'Neutral': 0,'Total':0}
    
    def add_sentences(self,sentences,results):
        for s, r in zip(sentences,results):
            self.add_sentence(s,r)

    def add_sentence(self,sentence,res):
        self.sentences.append( {'sentence':sentence,'label':res['label']} )
        self.sent_count[ res['label'] ] += 1
        self.sent_count['Total'] += 1
    
    def __str__(self):
        return self.get_stats()

    def get_stats(self):
        return f'''Positive count: {self.sent_count['Positive']}
                Negative count: {self.sent_count['Negative']}
                Neutral count: {self.sent_count['Neutral']}
                Total count: {self.sent_count['Total']}
            '''


from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda,RunnablePassthrough
from langchain.text_splitter import CharacterTextSplitter
import re
from dotenv import load_dotenv
import os

class CommentsSummary:
    def __init__(self,llm_model_name = 'llama3.2:3b'):
        self.create_summary_chains(llm_model_name)
        #Using langsmith for tracking llm 
        # if not load_dotenv('C:/env/.env'): print('Failed to load envirnoment variables')
        # os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        # os.environ['LANGCHAIN_PROJECT'] = "sent_analysis_web"
    
    def get_summary(self,comments,separator='<SEP>',complexity = 'one short paragraph'):
        splitter = CharacterTextSplitter(separator=separator,chunk_size=2000,chunk_overlap=0)
        chunks = splitter.split_text(comments)
        chunks_summaries = []
        for i,chunk in enumerate(chunks):
            chunk_info = f'the chunk {i+1} of {len(chunks)} ' if len(chunks) > 1 else 'a sequence'
            chunks_summaries.append(
                self.chain_chunks.invoke({'complexity':complexity,
                            'comments': chunk, 
                            'separator':separator,
                            'chunk_info':chunk_info }))
        if len(chunks_summaries) == 1: 
            return chunks_summaries[0]
        return self.summaries_chain.invoke( {'summaries':chunks_summaries,'separator':separator} )


    def create_summary_chains(self,llm_model_name = 'llama3.2:3b'):
        self.llm = ChatOllama(base_url='localhost:11434',model=llm_model_name)
        self.chain_chunks = self.create_chunks_chain()
        self.summaries_chain = self.create_summary_of_summaries_chain()

    def create_chunks_chain(self):
        prompt_str = (
            "Summarize {chunk_info} of comments in {complexity} giving a general idea of what all commentts are saying "
            "highlighting the overall sentiment of the sentences.\n" #Don't answer based on individual comments.
            "### Comments\n"
            "{comments}"
            "\n\n### Summary: "
        )
        prompt = PromptTemplate(input_variables=['complexity','comments','chunk_info'],template=prompt_str)
        return (
            {
                'complexity':RunnablePassthrough(),
                'comments': RunnableLambda(lambda x: self.format_comments(x['comments'],x['separator']) ),
                'chunk_info':RunnablePassthrough()
            }
            | prompt 
            | self.llm
            | StrOutputParser()
        )
    
    def create_summary_of_summaries_chain(self):
        prompt_str = (
            "The following texts are summaries of different comments of the same subject. " \
            "From this summaries provide a final summary based on all of them. Answer ONLY the final summary\n" \
            "### Summaries:\n" \
            "{summaries}" \
            "\nFinal Summary: "
        )
        prompt = PromptTemplate(input_variables=['summaries'],template=prompt_str)
        return (
            {'summaries':RunnableLambda(lambda x: self.format_summaries(x['summaries'],x['separator']))}
            | prompt
            | self.llm
            | StrOutputParser()
        )
    
    def format_comments(self,comments:str,separator:str):
        ''' Format a string containing comments separated by a separator token '''
        comments = re.sub(r'(\s)\1{2,}',r'\1',comments)
        comments = re.sub(separator,'\n\n',comments)
        comments = re.sub(r'\n{3,}',r'\n\n',comments)
        return comments.strip()
    
    def format_summaries(self,summaries:list,separator:str):
        ''' Format a list of summaries '''
        summaries = separator.join(summaries)
        return self.format_comments(summaries,separator)