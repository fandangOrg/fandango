'''
Created on 30 mar 2020

@author: daniele
'''
import torch
from pytorch_pretrained_bert.modeling import BertForPreTraining, BertModel
import torch.nn as nn
from fake_news_detection.config.constants import MAX_SEQ_LENGTH,\
    N_FEATURES_STYLE

'''
 - modello di DeepLearning
 
 Utilizzare dati testuale, quindi body e dati features quali n.aggettivi etc. 
 
'''

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

class BertStyleAndTextFeatures(BertForPreTraining):
    '''
        config - configurazione della rete, che tipo di modello utilizzare in partenza
        num_labels - numero di labels in output
        device - cuda o cpu
        features_style_number - il numero di features stylografiche 
        
       BERT + DENSESTYLE
         \     / 
        linearLayer
           |
        Fake/NoFake        
    
    '''
    OUTPUT_STYLE_LAYER=50
    TOKEN_PER_SENTENCE = 50

    def __init__(self, config,num_labels,device,features_style_number):
        
        super(BertStyleAndTextFeatures, self).__init__(config)
        self.bert = BertModel(config)
        l_params=list(self.bert.parameters())
        print("Layer",len(l_params))
        #,len(l_params[3:-1]),len(l_params[3:]))
        print("(1)number_parameter addestrabili",count_parameters(self.bert))
        #NON ADDESTRARE I LAYER SEGUENTI
        for param in l_params[:-3]:
            param.requires_grad = False
        print("(2)number_parameter addestrabili",count_parameters(self.bert))    
        self.device=device
        print("layersize output bert",config.hidden_size)
        ## TESTI SONO LUNGHI NOI CREAMI UN LSTM CHE DIVEDE IL TESTO IN FRASI
        self.lstm = nn.LSTM(config.hidden_size, config.hidden_size,3)
        
        self.dense_style = nn.Linear(features_style_number,self.OUTPUT_STYLE_LAYER)
        #self.dropout_style = nn.Dropout()
        #self.output_style = nn.Linear(300,50)
        self.classifier = nn.Linear(config.hidden_size+self.OUTPUT_STYLE_LAYER,num_labels)
        
        
        #uso devide
        #self.dense_style.to(device)
        #self.dropout_style.to(device)
        #self.output_style.to(device)
        #self.dropout = nn.Dropout(config.hidden_dropout_prob)
        #self.apply(self.init_weights)


    def _forward_style_base(self,input_ids_style):
        input_ids_style=input_ids_style.to(self.device)
        output=self.dense_style(input_ids_style)
        #output=self.dropout_style(output)
        #output=self.output_style(output)
        return output
        
    '''
     input_ids - id dei token delle parole dei testi
     features_style - vettore numerico delle features
     token_type_ids -  
     attention_mask - None, attention mask 
     head_mask      - None, head mask
    '''
    def forward(self, 
                input_ids,
                features_style, 
                token_type_ids=None, 
                attention_mask=None, 
                head_mask=None):
        # print(len(input_ids),input_ids)
        output_style=self._forward_style_base(features_style)
        
        #QUANTE NEWS STO ANALIZZANDO?
        
        number_news=len(input_ids)
        number_token=self.TOKEN_PER_SENTENCE
        number_sentence=MAX_SEQ_LENGTH//number_token
        ###########
        # max_seq_leng= 4 #token news totali
        # [[2 , 3 ,4,2],[6,4,7,2],[3,4,9,0],[2,4,5,0],[1,3,0,0]] # 
        # n_token=2
        # n_frasi=2
        #------------------------------#
        #===================================================================
        # [
        #  [ [2,3], [4,2] ],
        #  [[6,4] [7,2]],
        #  [ [3,4], [9,0]],
        #  [ [2,4],[5,0]],
        #  [ [1,3],[0,0]]
        #  ]
        #===================================================================
        input_ids=input_ids.reshape((number_news,number_sentence,number_token))
        ######################
        if token_type_ids is not None:
            token_type_ids=token_type_ids.reshape(number_news,number_sentence,number_token)
        else:
            token_type_ids=[None]*number_news
        if attention_mask is not None:
            attention_mask=attention_mask.reshape((number_news,number_sentence,number_token))
        else:
            attention_mask=[None]*number_news
        if head_mask is not None:
            head_mask =head_mask.reshape((number_news,number_sentence,number_token))
        else:
            head_mask=[None]*number_news
            
        #print(input_ids.shape)
        sentences_all=list()
        lstm_output=list()

        #===================================================================
        # [
        #  [ [2,3], [4,2] ],
        #  [[6,4] [7,2]],
        #  [ [3,4], [9,0]],
        #  [ [2,4],[5,0]],
        #  [ [1,3],[0,0]]
        #  ]
        #===================================================================
                
        #tratta ogni documento, come un insieme di documenti, e convertili con bert
        for article_index in range(0,len(input_ids)):
            #print(input_ids[article_index].shape)
            a=input_ids[article_index]
            mask=attention_mask[article_index]
            outputs = self.bert(a, token_type_ids=token_type_ids[article_index], attention_mask=mask)
            sentences_all.append(outputs[1])

        #sentences_all=
        # [
        #  [ [243,532,2.4....,0.3] {lunghezza del vettore 768}, [3.2, 0.5, .3 ,.4 ..., .2] {768 lungo} ],
        #  [[6,4....] [7,2...]],
        #  [ [3,4...],[9,0...]],
        #  [ [2,4...],[5,0...]],
        #  [ [1,3...],[0,0...]]
        #  ]
        # shape senteces_all.shape =  5,2,768
        #===================================================================
        
        
#===============================================================================
#         anlizza frase per frase e articolo per artico

#         for article_index in range(0,len(input_ids)):
#             #print(input_ids[article_index].shape)
#             sentences=list()
#             for sentence_index in range(0,len(input_ids[article_index])):
#                 sentence=input_ids[article_index][sentence_index].to(self.device).reshape(-1,number_token)
#                 mask_tmp=attention_mask[article_index][sentence_index].to(self.device).reshape(-1,number_token)
# #                print(sentence.shape)
#                 outputs = self.bert(sentence, token_type_ids=token_type_ids[article_index], attention_mask=mask_tmp)
#                 sentences.append(outputs[1])
#                 del sentence
#                 del outputs
#                 del mask_tmp
#             x= torch.stack(sentences)
#             x=x.permute((1,0,2))
#            tensor_of_sentences=torch.stack(sentences)
#            tensor_of_sentences=x.to(self.device)
#            pooled_output = self.lstm(tensor_of_sentences)
#===============================================================================
            
            # [.3,  |  [.1
            #  .3   |   .5
            #  .2   |   .5
            #  .1]  |   .0]
            #
            pooled_output = self.lstm(torch.stack(sentences_all))
            #pooled_output = self.lstm(tensor_of_sentences)
            output, (h_n, c_n) = pooled_output
            for news in output:
                lstm_output.append(news[-1])
                
            #lstm_output=
            # [
            #   [243,532,2.4....,0.3] {lunghezza del vettore 768},
            #   [243,532,2.4....,0.3] {lunghezza del vettore 768},
            #   [.43,.32,2.4....,0.3] {lunghezza del vettore 768},
            #   [.3,5.5,2.4....,0.3] {lunghezza del vettore 768}
            #   [2.3,5.2,2.4....,0.3] {lunghezza del vettore 768}
            #  ]
            # shape senteces_all.shape =  5,1,768 -- 5,768
            #===================================================================
            
            del output
            del pooled_output
            sentences_all.clear()
            del sentences_all[:] 
            torch.cuda.empty_cache()
            
            ### --- ### --- ### --- ### --- ### --- ###
            #===================================================================
            # a=input_ids[article_index].to(self.device)
            # print(a.shape)
            # mask=attention_mask[article_index].to(self.device)
            # #self.bert.to('cpu')
            # outputs = self.bert(a, token_type_ids=token_type_ids[article_index], attention_mask=mask)
            # del a
            # sentences.append(outputs[1])
            #===================================================================

        #print(outputs[1].shape,outputs[1])
        #print("--->output",output.shape)
        #print("--->lstm_output",torch.stack(lstm_output).shape)
        pooled_output = torch.stack(lstm_output)
        #shape 5, 1 ,768 
        
        all_features=(torch.cat([output_style, pooled_output], dim=-1))
        #shape 5, 1, 768+50 
        
        
            #===================================================================
            # print(type(outputs[0]),type(outputs[1]))
            # pooled_output = outputs[1].reshape((-1,5,8))
            # print(pooled_output[0].shape)
            #===================================================================
            #pooled_output = self.dropout(pooled_output)
        #print("pooled_output[0].shape",pooled_output.shape)
        logits = self.classifier(all_features)
        
        #logits = 
        # [[0,3,0-2] ,[0,1] ,[4.3] ,[] , []] 
        
        #print(logits.shape)
        #print(logits)
        return logits
 
 
if __name__ == '__main__':
    
    model = BertStyleAndTextFeatures.from_pretrained("bert-base-multilingual-uncased" ,num_labels=2,device='cuda',features_style_number=N_FEATURES_STYLE)
    
    
    
    
    