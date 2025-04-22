import openai
from flask import current_app
import logging

class OpenAIClient:
    def __init__(self, api_key=None, model=None):
        """初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key or current_app.config.get('OPENAI_API_KEY')
        self.model = model or current_app.config.get('DEFAULT_MODEL')
        self.client = openai.OpenAI(api_key=self.api_key)
        
    def get_evaluation(self, content, fewshot_examples, dimension):
        """使用few-shot示例评估内容
        
        Args:
            content: 待评估内容
            fewshot_examples: 专家评估的few-shot示例列表
            dimension: 评估维度信息
            
        Returns:
            dict: 包含评分和理由的评估结果
        """
        try:
            # 构建评估提示词
            prompt = self._build_evaluation_prompt(
                content, fewshot_examples, dimension
            )
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI评估专家，根据提供的示例和标准进行评估。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # 低温度以确保一致性
            )
            
            # 解析结果
            result = response.choices[0].message.content
            parsed_result = self._parse_evaluation_result(result)
            return parsed_result
            
        except Exception as e:
            logging.error(f"OpenAI API调用失败: {str(e)}")
            return {"error": str(e)}
    
    def _build_evaluation_prompt(self, content, fewshot_examples, dimension):
        """构建评估提示词
        
        Args:
            content: 待评估内容
            fewshot_examples: 专家评估示例
            dimension: 评估维度
            
        Returns:
            str: 完整的评估提示词
        """
        prompt = f"## 评估维度\n{dimension.name}: {dimension.description}\n\n"
        prompt += f"## 评分标准\n{dimension.scoring_guide}\n\n"
        
        # 添加few-shot示例
        prompt += "## 专家评估示例\n"
        for i, example in enumerate(fewshot_examples, 1):
            prompt += f"### 示例 {i}\n"
            prompt += f"内容:\n{example.content}\n\n"
            prompt += f"评分: {example.score}/10\n"
            prompt += f"评分理由: {example.rationale}\n\n"
        
        # 添加待评估内容
        prompt += "## 待评估内容\n"
        prompt += f"{content}\n\n"
        
        # 请求评估格式
        prompt += "## 请进行评估\n"
        prompt += "请参考上面的示例，对待评估内容进行评分和分析。\n"
        prompt += "以下格式回复:\n"
        prompt += "评分: [1-10的分数]\n"
        prompt += "评分理由: [详细解释为什么给出这个评分]\n"
        
        return prompt
    
    def _parse_evaluation_result(self, result):
        """解析评估结果
        
        Args:
            result: OpenAI API返回的文本结果
            
        Returns:
            dict: 包含评分和理由的字典
        """
        lines = result.strip().split('\n')
        score = None
        rationale = []
        
        parsing_rationale = False
        
        for line in lines:
            if line.startswith("评分:"):
                try:
                    # 提取分数
                    score_text = line.replace("评分:", "").strip()
                    score = int(score_text.split('/')[0]) if '/' in score_text else int(score_text)
                except ValueError:
                    score = 0
            elif line.startswith("评分理由:"):
                parsing_rationale = True
                rationale_part = line.replace("评分理由:", "").strip()
                if rationale_part:
                    rationale.append(rationale_part)
            elif parsing_rationale:
                rationale.append(line.strip())
        
        return {
            "score": score,
            "rationale": " ".join(rationale)
        }