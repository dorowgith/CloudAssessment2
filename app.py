# Flask app will be initialized here
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os # For a more robust secret key generation if needed
from datetime import datetime, timedelta
import json

SCORING_MULTIPLIERS = {
    "total": 1.0,
    "parcial": 0.5,
    "nao_atendida": 0.0,
    "nao_se_aplica": None
}

# Definir CATEGORY_BASELINES antes de tudo
CATEGORY_BASELINES = {
    "Arquitetura": 70.0,
    "Resiliência": 75.0,
    "Cyber Segurança": 80.0,
    "Governança": 65.0,
    "FinOps": 60.0
}

# Categorias e suas questões
CATEGORIES_DATA = [
    {
        "id": "arquitetura",
        "name": "Arquitetura",
        "description": "Avaliação da arquitetura da solução em nuvem",
        "baseline": CATEGORY_BASELINES["Arquitetura"],
        "questions": [
            {"id": "arq1", "text": "A arquitetura da solução está bem definida e documentada?", "weight": 5},
            {"id": "arq2", "text": "A solução utiliza componentes e serviços adequados para os requisitos?", "weight": 4},
            {"id": "arq3", "text": "A escalabilidade da arquitetura foi considerada?", "weight": 4}
        ]
    },
    {
        "id": "resiliencia",
        "name": "Resiliência",
        "description": "Avaliação da resiliência e disponibilidade da solução",
        "baseline": CATEGORY_BASELINES["Resiliência"],
        "questions": [
            {"id": "res1", "text": "Existem mecanismos de backup e restauração de dados definidos e testados?", "weight": 5},
            {"id": "res2", "text": "A solução possui alta disponibilidade e tolerância a falhas?", "weight": 5},
            {"id": "res3", "text": "Existe um plano de recuperação de desastres (DRP)?", "weight": 3}
        ]
    },
    {
        "id": "cyber_seguranca",
        "name": "Cyber Segurança",
        "description": "Avaliação da segurança e proteção da solução",
        "baseline": CATEGORY_BASELINES["Cyber Segurança"],
        "questions": [
            {"id": "sec1", "text": "As melhores práticas de segurança foram aplicadas no desenvolvimento e configuração?", "weight": 5},
            {"id": "sec2", "text": "Existem controles de acesso e autenticação robustos?", "weight": 4},
            {"id": "sec3", "text": "A solução é monitorada quanto a atividades suspeitas e vulnerabilidades?", "weight": 4}
        ]
    },
    {
        "id": "governanca",
        "name": "Governança",
        "description": "Avaliação da governança e gestão da solução",
        "baseline": CATEGORY_BASELINES["Governança"],
        "questions": [
            {"id": "gov1", "text": "Os papéis e responsabilidades relacionados à operação da solução estão claros?", "weight": 4},
            {"id": "gov2", "text": "Existem processos para gestão de mudanças e configuração?", "weight": 4},
            {"id": "gov3", "text": "A conformidade com políticas e regulações é auditada?", "weight": 3}
        ]
    },
    {
        "id": "finops",
        "name": "FinOps",
        "description": "Avaliação da gestão de custos e otimização financeira",
        "baseline": CATEGORY_BASELINES["FinOps"],
        "questions": [
            {"id": "fin1", "text": "Existe um acompanhamento e otimização contínua dos custos da solução em nuvem?", "weight": 5},
            {"id": "fin2", "text": "As instâncias e serviços estão dimensionados corretamente para evitar desperdícios?", "weight": 4},
            {"id": "fin3", "text": "Há visibilidade sobre os gastos e alocação de custos por centro de custo ou projeto?", "weight": 3}
        ]
    }
]

# Templates são apenas referências às categorias que queremos usar
TEMPLATES = [
    {
        "id": "template_completo",
        "name": "Assessment Completo",
        "description": "Avaliação completa incluindo todas as categorias",
        "category_ids": ["arquitetura", "resiliencia", "cyber_seguranca", "governanca", "finops"]
    },
    {
        "id": "template_seguranca",
        "name": "Assessment de Segurança",
        "description": "Foco em segurança e governança",
        "category_ids": ["cyber_seguranca", "governanca"]
    },
    {
        "id": "template_infra",
        "name": "Assessment de Infraestrutura",
        "description": "Foco em arquitetura e resiliência",
        "category_ids": ["arquitetura", "resiliencia"]
    }
]

# Simulação de banco de dados com dados de exemplo
COMPLETED_ASSESSMENTS = []

app = Flask(__name__)
# IMPORTANT: Add a secret key for session management
app.secret_key = os.urandom(24) # Or a fixed string for development: 'your_very_secret_key'

@app.route('/')
def index():
    if not COMPLETED_ASSESSMENTS:
        generate_sample_completed_assessments()
    
    # Calcular métricas básicas
    total_assessments = len(TEMPLATES) + len(CATEGORIES_DATA)
    completed_assessments = len(COMPLETED_ASSESSMENTS)
    
    # Preparar dados para os gráficos
    dates = [assessment['date'] for assessment in COMPLETED_ASSESSMENTS]
    scores = [assessment['score'] for assessment in COMPLETED_ASSESSMENTS]
    
    # Calcular distribuição por categoria
    categories = [cat['name'] for cat in CATEGORIES_DATA]
    category_counts = [sum(1 for a in COMPLETED_ASSESSMENTS if cat in a['categories']) 
                      for cat in categories]
    
    # Calcular pontuações médias por categoria
    category_scores = []
    for category in categories:
        category_assessments = [a for a in COMPLETED_ASSESSMENTS if category in a['categories']]
        if category_assessments:
            avg_score = sum(a['score'] for a in category_assessments) / len(category_assessments)
            category_scores.append(round(avg_score, 1))
        else:
            category_scores.append(0)
    
    # Preparar dados de tendências
    trend_dates = sorted(list(set(dates)))[-6:]  # Últimos 6 períodos
    trend_datasets = []
    for category in categories:
        dataset = {
            'label': category,
            'data': [],
            'borderColor': get_category_color(category),
            'fill': False
        }
        for date in trend_dates:
            relevant_assessments = [a for a in COMPLETED_ASSESSMENTS 
                                  if a['date'] == date and category in a['categories']]
            if relevant_assessments:
                avg = sum(a['score'] for a in relevant_assessments) / len(relevant_assessments)
                dataset['data'].append(round(avg, 1))
            else:
                dataset['data'].append(None)
        trend_datasets.append(dataset)

    # Calcular métricas gerais
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    completion_rate = round((len([a for a in COMPLETED_ASSESSMENTS if a['status'] == 'Concluído']) / total_assessments) * 100 if total_assessments > 0 else 0, 1)
    
    # Calcular taxa de melhoria
    if len(scores) >= 2:
        current_avg = sum(scores[-len(scores)//2:]) / (len(scores)//2)
        previous_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
        improvement_rate = round(((current_avg - previous_avg) / previous_avg) * 100, 1) if previous_avg > 0 else 0
    else:
        improvement_rate = 0

    return render_template('index.html',
                         dates=dates,
                         scores=scores,
                         categories=categories,
                         category_counts=category_counts,
                         category_scores=category_scores,
                         trend_dates=trend_dates,
                         trend_datasets=trend_datasets,
                         total_assessments=total_assessments,
                         completed_assessments=completed_assessments,
                         avg_score=avg_score,
                         completion_rate=completion_rate,
                         improvement_rate=improvement_rate,
                         category_baselines=[CATEGORY_BASELINES.get(cat, 0) for cat in categories])

@app.route('/templates')
def list_templates():
    # Preparar dados dos templates para exibição
    templates_info = []
    
    for template in TEMPLATES:
        # Buscar informações das categorias referenciadas
        categories = []
        total_questions = 0
        
        for category_id in template['category_ids']:
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                categories.append(category['name'])
                total_questions += len(category['questions'])
        
        template_info = {
            'id': template['id'],
            'name': template['name'],
            'description': template['description'],
            'categories': categories,
            'total_questions': total_questions
        }
        templates_info.append(template_info)
    
    return render_template('list_templates.html', 
                         templates=templates_info,
                         categories=CATEGORIES_DATA)

@app.route('/templates/create', methods=['POST'])
def create_template():
    try:
        print("\n=== Creating new template ===")
        data = request.json
        name = data.get('name')
        description = data.get('description')
        selected_categories = data.get('selectedCategories', [])
        
        if not name or not selected_categories:
            return jsonify({'error': 'Nome e pelo menos uma categoria são obrigatórios'}), 400
        
        # Validar que todas as categorias existem
        category_ids = []
        for selected in selected_categories:
            category_id = selected.get('id')
            if not category_id:
                return jsonify({'error': 'ID de categoria inválido'}), 400
                
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if not category:
                return jsonify({'error': f'Categoria não encontrada: {category_id}'}), 400
                
            if not category.get('questions'):
                return jsonify({'error': f'A categoria {category["name"]} não possui questões definidas'}), 400
                
            category_ids.append(category_id)
        
        # Criar novo template
        template_id = f"template_{len(TEMPLATES) + 1}"
        new_template = {
            'id': template_id,
            'name': name,
            'description': description,
            'category_ids': category_ids  # Usar a lista de IDs validados
        }
        
        print(f"\nTemplate creation summary:")
        print(f"- Name: {new_template['name']}")
        print(f"- Description: {new_template['description']}")
        print(f"- Categories: {new_template['category_ids']}")
        
        TEMPLATES.append(new_template)
        
        # Preparar resposta com informações completas
        categories = []
        total_questions = 0
        for category_id in new_template['category_ids']:
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                categories.append(category['name'])
                total_questions += len(category.get('questions', []))
        
        return jsonify({
            'success': True,
            'template': {
                'id': template_id,
                'name': name,
                'description': description,
                'categories': categories,
                'total_questions': total_questions
            }
        }), 201
        
    except Exception as e:
        print(f"\nError creating template: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro ao criar template: ' + str(e)}), 500

@app.route('/templates/delete/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    try:
        print(f"\n=== Deleting template {template_id} ===")
        
        # Verificar se existem assessments usando este template
        assessments_with_template = [a for a in COMPLETED_ASSESSMENTS if a.get('template_id') == template_id]
        if assessments_with_template:
            print(f"Found {len(assessments_with_template)} assessments using this template")
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir este template pois existem assessments que o utilizam.'
            })
        
        # Primeiro, tentar encontrar e remover dos templates personalizados
        template = next((t for t in TEMPLATES if t['id'] == template_id), None)
        if template:
            TEMPLATES.remove(template)
            print(f"Removed template: {template['name']}")
            return jsonify({'success': True, 'message': 'Template excluído com sucesso'}), 200
        
        print(f"Template not found with ID: {template_id}")
        return jsonify({'error': 'Template não encontrado'}), 404
        
    except Exception as e:
        print(f"Error deleting template: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro ao excluir template'}), 500

@app.route('/start_assessment/<template_id>')
def start_assessment(template_id):
    try:
        print(f"\n=== Starting assessment for template_id: {template_id} ===")
        
        if not template_id:
            print("No template ID provided")
            flash('ID do template não fornecido', 'error')
            return redirect(url_for('list_templates'))
        
        # Encontrar o template
        template = next((t for t in TEMPLATES if t['id'] == template_id), None)
        if not template:
            print(f"Template not found for ID: {template_id}")
            print("Available templates:", [t['id'] for t in TEMPLATES])
            flash('Template não encontrado', 'error')
            return redirect(url_for('list_templates'))
        
        print(f"\nFound template:")
        print(f"- ID: {template['id']}")
        print(f"- Name: {template['name']}")
        print(f"- Category IDs: {template.get('category_ids', [])}")
        
        # Verificar se o template tem category_ids
        if not template.get('category_ids'):
            print("Template has no category_ids")
            flash('Template inválido: nenhuma categoria definida', 'error')
            return redirect(url_for('list_templates'))
        
        # Debug: Mostrar todas as categorias disponíveis
        print("\nAll available categories:")
        for c in CATEGORIES_DATA:
            print(f"- ID: {c['id']}, Name: {c['name']}")
        
        # Buscar categorias e suas questões
        print("\nProcessing categories:")
        categories = []
        for category_id in template['category_ids']:
            print(f"\nProcessing category ID: {category_id}")
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                print(f"Found category: {category['name']}")
                print(f"Questions in category: {len(category.get('questions', []))}")
                
                # Verificar se a categoria tem questões
                if not category.get('questions'):
                    print(f"Warning: Category {category['name']} has no questions")
                    continue
                
                # Verificar estrutura das questões
                valid_questions = []
                for q in category['questions']:
                    if not isinstance(q, dict):
                        print(f"Warning: Invalid question type: {type(q)}")
                        continue
                        
                    if 'id' not in q or 'text' not in q:
                        print(f"Warning: Invalid question structure: {q}")
                        continue
                        
                    valid_questions.append(q)
                
                if valid_questions:  # Só adiciona a categoria se tiver questões válidas
                    category_data = {
                        'id': category['id'],
                        'name': category['name'],
                        'questions': valid_questions,
                        'baseline': category.get('baseline', CATEGORY_BASELINES.get(category['name'], 70))
                    }
                    categories.append(category_data)
                    print(f"Added category with {len(valid_questions)} valid questions")
                else:
                    print(f"Warning: No valid questions found in category {category['name']}")
            else:
                print(f"Category not found with ID: {category_id}")
        
        if not categories:
            print("\nNo valid categories found in template")
            flash('Nenhuma categoria válida encontrada para este template. Verifique se as categorias têm questões válidas.', 'error')
            return redirect(url_for('list_templates'))
        
        # Criar estrutura do template
        template_data = {
            'id': template['id'],
            'name': template['name'],
            'categories': categories
        }
        
        print("\nTemplate data prepared successfully:")
        print(f"- Template: {template_data['name']}")
        print(f"- Categories: {len(template_data['categories'])}")
        print(f"- Total questions: {sum(len(c['questions']) for c in template_data['categories'])}")
        
        # Debug: Verificar estrutura final do template_data
        print("\nFinal template_data structure:")
        print(f"template_data: {template_data}")
        
        return render_template('form.html', 
                             categories=[template_data],
                             debug=True)  # Ativar informações de debug
        
    except Exception as e:
        print("\n=== Error in start_assessment ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        flash('Erro ao iniciar assessment: ' + str(e), 'error')
        return redirect(url_for('list_templates'))

@app.route('/completed-assessments')
def completed_assessments():
    # Limpar dados de exemplo existentes e gerar novos
    COMPLETED_ASSESSMENTS.clear()
    generate_sample_completed_assessments()
    
    return render_template('completed_assessments.html',
                         completed_assessments=COMPLETED_ASSESSMENTS)

@app.route('/dashboard')
def dashboard():
    # Limpar dados de exemplo existentes e gerar novos
    COMPLETED_ASSESSMENTS.clear()
    generate_sample_completed_assessments()

    # Preparar dados para os gráficos
    dates = [assessment['date'] for assessment in COMPLETED_ASSESSMENTS]
    scores = [assessment['score'] for assessment in COMPLETED_ASSESSMENTS]
    
    # Calcular distribuição por categoria
    categories = [cat['name'] for cat in CATEGORIES_DATA]
    category_counts = [sum(1 for a in COMPLETED_ASSESSMENTS if cat in a['categories']) 
                      for cat in categories]
    
    # Calcular pontuações médias por categoria
    category_scores = []
    for category in categories:
        category_assessments = [a for a in COMPLETED_ASSESSMENTS if category in a['categories']]
        if category_assessments:
            avg_score = sum(a['score'] for a in category_assessments) / len(category_assessments)
            category_scores.append(round(avg_score, 1))
        else:
            category_scores.append(0)
    
    # Preparar dados de tendências
    trend_dates = sorted(list(set(dates)))[-6:]  # Últimos 6 períodos
    trend_datasets = []
    for category in categories:
        dataset = {
            'label': category,
            'data': [],
            'borderColor': get_category_color(category),
            'fill': False
        }
        for date in trend_dates:
            relevant_assessments = [a for a in COMPLETED_ASSESSMENTS 
                                  if a['date'] == date and category in a['categories']]
            if relevant_assessments:
                avg = sum(a['score'] for a in relevant_assessments) / len(relevant_assessments)
                dataset['data'].append(round(avg, 1))
            else:
                dataset['data'].append(None)
        trend_datasets.append(dataset)

    # Calcular métricas gerais
    total_assessments = len(COMPLETED_ASSESSMENTS)
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    completion_rate = round((len([a for a in COMPLETED_ASSESSMENTS if a['status'] == 'Concluído']) / total_assessments) * 100 if total_assessments > 0 else 0, 1)
    
    # Calcular taxa de melhoria (comparando com período anterior)
    if len(scores) >= 2:
        current_avg = sum(scores[-len(scores)//2:]) / (len(scores)//2)
        previous_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
        improvement_rate = round(((current_avg - previous_avg) / previous_avg) * 100, 1) if previous_avg > 0 else 0
    else:
        improvement_rate = 0

    return render_template('dashboard.html',
                         dates=dates,
                         scores=scores,
                         categories=categories,
                         category_counts=category_counts,
                         category_scores=category_scores,
                         trend_dates=trend_dates,
                         trend_datasets=trend_datasets,
                         total_assessments=total_assessments,
                         avg_score=avg_score,
                         completion_rate=completion_rate,
                         improvement_rate=improvement_rate)

@app.route('/save_progress', methods=['POST'])
def save_progress():
    try:
        print("\n=== Starting save_progress ===")
        
        # Identificar o template e assessment
        template_id = request.form.get('template_id')
        assessment_id = request.form.get('assessment_id')
        
        print(f"Template ID: {template_id}")
        print(f"Assessment ID: {assessment_id}")
        
        if not template_id:
            print("No template ID provided")
            return jsonify({'success': False, 'error': 'Template ID não fornecido'})
        
        # Encontrar o template
        template = next((t for t in TEMPLATES if t['id'] == template_id), None)
        if not template:
            print(f"Template not found for ID: {template_id}")
            print("Available templates:", [t['id'] for t in TEMPLATES])
            return jsonify({'success': False, 'error': 'Template não encontrado'})
        
        print(f"\nFound template: {template['name']}")
        print(f"Template categories: {template['category_ids']}")
        
        # Debug: Mostrar todas as categorias disponíveis
        print("\nAll available categories:")
        for c in CATEGORIES_DATA:
            print(f"- ID: {c['id']}, Name: {c['name']}")
        
        # Coletar respostas atuais
        responses = {}
        print("\nCollecting responses:")
        for category_id in template['category_ids']:
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                print(f"\nProcessing category: {category['name']}")
                for question in category['questions']:
                    answer = request.form.get(question['id'])
                    if answer:
                        responses[question['id']] = answer
                        print(f"- Question {question['id']}: {answer}")
        
        print(f"\nCollected {len(responses)} responses")
        
        # Se já existe um assessment em andamento, atualizar
        if assessment_id:
            print(f"\nTrying to update existing assessment {assessment_id}")
            assessment = next((a for a in COMPLETED_ASSESSMENTS if str(a['id']) == str(assessment_id)), None)
            if assessment:
                print("Found existing assessment")
                print(f"Previous responses: {len(assessment.get('responses', {}))}")
                assessment['responses'] = responses
                assessment['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"Updated with {len(responses)} responses")
                return jsonify({'success': True, 'assessment_id': assessment['id']})
            else:
                print("Existing assessment not found")
        
        # Criar novo assessment em andamento
        print("\nCreating new assessment")
        new_assessment_id = len(COMPLETED_ASSESSMENTS) + 1
        new_assessment = {
            'id': new_assessment_id,
            'template_id': template_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'name': template['name'],
            'categories': [next((c['name'] for c in CATEGORIES_DATA if c['id'] == cat_id), None) 
                         for cat_id in template['category_ids']],
            'responses': responses,
            'status': 'Em Andamento',
            'score': 0,
            'category_scores': {}  # Inicializar scores vazios
        }
        
        # Debug: Verificar estrutura do novo assessment
        print("\nNew assessment structure:")
        for key, value in new_assessment.items():
            if key == 'responses':
                print(f"- {key}: {len(value)} responses")
            else:
                print(f"- {key}: {value}")
        
        COMPLETED_ASSESSMENTS.append(new_assessment)
        print(f"Created new assessment with ID {new_assessment_id}")
        
        return jsonify({
            'success': True,
            'assessment_id': new_assessment_id
        })
        
    except Exception as e:
        print("\n=== Error in save_progress ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Erro ao salvar progresso'})

@app.route('/continue_assessment/<int:assessment_id>')
def continue_assessment(assessment_id):
    try:
        print("\n=== Starting continue_assessment ===")
        print(f"Assessment ID: {assessment_id}")
        print(f"Type of assessment_id: {type(assessment_id)}")
        
        # Debug: Mostrar todos os assessments disponíveis
        print("\nAll available assessments:")
        for a in COMPLETED_ASSESSMENTS:
            print(f"- ID: {a['id']} ({type(a['id'])}), Name: {a['name']}, Status: {a.get('status')}")
        
        # Encontrar o assessment
        assessment = next((a for a in COMPLETED_ASSESSMENTS if a['id'] == assessment_id), None)
        if not assessment:
            print(f"\nAssessment not found with ID {assessment_id}")
            flash('Assessment não encontrado', 'error')
            return redirect(url_for('list_templates'))
        
        print("\nFound assessment:")
        print(f"- ID: {assessment['id']}")
        print(f"- Name: {assessment['name']}")
        print(f"- Template ID: {assessment.get('template_id')}")
        print(f"- Status: {assessment.get('status')}")
        print(f"- Categories: {assessment.get('categories', [])}")
        print(f"- Responses: {len(assessment.get('responses', {}))}")
        
        # Encontrar o template
        template = next((t for t in TEMPLATES if t['id'] == assessment.get('template_id')), None)
        if not template:
            print(f"\nTemplate not found with ID: {assessment.get('template_id')}")
            print("Available templates:", [t['id'] for t in TEMPLATES])
            flash('Template não encontrado', 'error')
            return redirect(url_for('list_templates'))
        
        print("\nFound template:")
        print(f"- ID: {template['id']}")
        print(f"- Name: {template['name']}")
        print(f"- Category IDs: {template['category_ids']}")
        
        # Preparar dados do template com as categorias
        template_data = {
            'id': template['id'],
            'name': template['name'],
            'categories': []
        }
        
        # Debug: Mostrar todas as categorias disponíveis
        print("\nAll available categories:")
        for c in CATEGORIES_DATA:
            print(f"- ID: {c['id']}, Name: {c['name']}")
        
        # Adicionar categorias com suas questões
        print("\nProcessing categories:")
        for category_id in template['category_ids']:
            print(f"\nProcessing category ID: {category_id}")
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                print(f"Found category: {category['name']}")
                category_data = {
                    'id': category['id'],
                    'name': category['name'],
                    'questions': category['questions'],
                    'baseline': category.get('baseline', CATEGORY_BASELINES.get(category['name'], 70))
                }
                template_data['categories'].append(category_data)
                print(f"Added category with {len(category['questions'])} questions")
            else:
                print(f"Category not found with ID: {category_id}")
        
        if not template_data['categories']:
            print("\nNo categories found in template")
            flash('Erro ao carregar categorias do template', 'error')
            return redirect(url_for('list_templates'))
        
        print("\nTemplate data prepared successfully:")
        print(f"- Template: {template_data['name']}")
        print(f"- Categories: {len(template_data['categories'])}")
        print(f"- Total questions: {sum(len(c['questions']) for c in template_data['categories'])}")
        
        # Debug: Verificar as respostas salvas
        saved_responses = assessment.get('responses', {})
        print("\nSaved responses:")
        print(f"- Number of responses: {len(saved_responses)}")
        print(f"- Response keys: {list(saved_responses.keys())}")
        
        return render_template('form.html', 
                             categories=[template_data],
                             assessment_id=assessment_id,
                             saved_responses=saved_responses)
                             
    except Exception as e:
        print("\n=== Error in continue_assessment ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        flash('Erro ao carregar assessment', 'error')
        return redirect(url_for('list_templates'))

@app.route('/submit', methods=['POST'])
def submit_assessment():
    try:
        print("\n=== Processing assessment submission ===")
        
        # Verificar se é um assessment existente
        assessment_id = request.form.get('assessment_id')
        template_id = request.form.get('template_id')
        
        print(f"Template ID: {template_id}")
        print(f"Assessment ID: {assessment_id}")
        
        if assessment_id:
            # Remover o assessment em andamento
            assessment = next((a for a in COMPLETED_ASSESSMENTS if str(a['id']) == str(assessment_id)), None)
            if assessment:
                COMPLETED_ASSESSMENTS.remove(assessment)
                print(f"Removed in-progress assessment {assessment_id}")
        
        # Identificar o template
        if not template_id:
            print("No template ID provided")
            raise ValueError("Template ID não fornecido")
        
        # Encontrar o template
        template = next((t for t in TEMPLATES if t['id'] == template_id), None)
        if not template:
            print(f"Template not found for ID: {template_id}")
            print("Available templates:", [t['id'] for t in TEMPLATES])
            raise ValueError("Template não encontrado")
        
        print(f"Found template: {template['name']}")
        
        # Inicializar pontuações
        category_scores = {}
        total_weighted_points = 0
        total_possible_weighted_points = 0
        
        # Calcular pontuação por categoria
        for category_id in template['category_ids']:
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                category_weighted_points = 0
                category_possible_weighted_points = 0
                questions_not_applicable = 0
                
                for question in category['questions']:
                    answer = request.form.get(question['id'])
                    weight = question.get('weight', 1)
                    
                    if answer == 'nao_se_aplica':
                        questions_not_applicable += 1
                        continue
                    
                    multiplier = SCORING_MULTIPLIERS.get(answer, 0)
                    category_weighted_points += weight * multiplier
                    category_possible_weighted_points += weight
                
                if category_possible_weighted_points > 0:
                    category_score = (category_weighted_points / category_possible_weighted_points) * 100
                else:
                    category_score = 0
                
                category_scores[category_id] = {
                    'score': round(category_score, 1),
                    'weighted_points': category_weighted_points,
                    'possible_weighted_points': category_possible_weighted_points,
                    'questions_not_applicable': questions_not_applicable
                }
                
                total_weighted_points += category_weighted_points
                total_possible_weighted_points += category_possible_weighted_points
        
        # Calcular pontuação final
        final_score = (total_weighted_points / total_possible_weighted_points * 100) if total_possible_weighted_points > 0 else 0
        
        # Criar novo assessment concluído
        new_assessment = {
            'id': len(COMPLETED_ASSESSMENTS) + 1,
            'template_id': template_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'name': template['name'],
            'categories': [next((c['name'] for c in CATEGORIES_DATA if c['id'] == cat_id), None) 
                         for cat_id in template['category_ids']],
            'category_scores': category_scores,
            'score': round(final_score, 1),
            'status': 'Concluído',
            'responses': {k: v for k, v in request.form.items() if k not in ['template_id', 'assessment_id']}
        }
        
        COMPLETED_ASSESSMENTS.append(new_assessment)
        print(f"Created completed assessment with ID {new_assessment['id']}")
        
        return redirect(url_for('show_results', assessment_id=new_assessment['id']))
        
    except Exception as e:
        print(f"\nError submitting assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Erro ao submeter assessment', 'error')
        return redirect(url_for('list_templates'))

@app.route('/results')
@app.route('/results/<int:assessment_id>')
def show_results(assessment_id=None):
    try:
        print("\n=== Showing assessment results ===")
        results = None
        
        # Se não foi fornecido ID, tentar pegar da sessão
        if assessment_id is None:
            assessment_id = session.get('last_assessment_id')
            print(f"No assessment_id in URL, got from session: {assessment_id}")
        
        # Se temos um ID (da URL ou sessão), buscar o assessment
        if assessment_id:
            print(f"Looking for assessment with ID: {assessment_id}")
            assessment = next((a for a in COMPLETED_ASSESSMENTS if a['id'] == assessment_id), None)
            
            if not assessment:
                print(f"Assessment not found with ID: {assessment_id}")
                flash('Assessment não encontrado', 'error')
                return redirect(url_for('completed_assessments'))
            
            print(f"Found assessment: {assessment['name']}")
            print(f"Assessment data: {assessment}")
            
            # Garantir que todos os dados necessários estão presentes
            required_keys = ['name', 'category_scores', 'score', 'total_points', 'total_possible']
            missing_keys = [key for key in required_keys if key not in assessment]
            
            if missing_keys:
                print(f"Missing required keys in assessment data: {missing_keys}")
                print(f"Available keys: {list(assessment.keys())}")
                
                # Tentar reconstruir dados faltantes
                if 'category_scores' not in assessment and 'categories' in assessment:
                    assessment['category_scores'] = {}
                    for category in assessment['categories']:
                        assessment['category_scores'][category] = {
                            'name': category,
                            'points': 0,
                            'total_possible': 100,
                            'questions_answered': 0,
                            'questions_not_applicable': 0,
                            'total_questions': 0,
                            'percentage': 0
                        }
                
                if 'total_points' not in assessment and 'score' in assessment:
                    assessment['total_points'] = assessment['score']
                    assessment['total_possible'] = 100
                
                # Verificar novamente após tentar reconstruir
                missing_keys = [key for key in required_keys if key not in assessment]
                if missing_keys:
                    print(f"Still missing keys after reconstruction: {missing_keys}")
                    flash('Dados do assessment incompletos', 'error')
                    return redirect(url_for('completed_assessments'))
            
            results = {
                'template_name': assessment['name'],
                'category_scores': assessment['category_scores'],
                'final_score': assessment['score'],
                'total_points': assessment['total_points'],
                'total_possible': assessment['total_possible']
            }
            
            print(f"Prepared results data: {results}")
        else:
            print("No assessment_id available, checking session data")
            # Usar os resultados da sessão (para assessments recém-completados)
            results = session.get('assessment_results')
            
            if not results:
                print("No results found in session")
                flash('Nenhum resultado encontrado na sessão', 'error')
                return redirect(url_for('completed_assessments'))
            
            print("Found results in session")
            assessment_id = session.get('last_assessment_id')
        
        if not results:
            print("No results data available")
            flash('Dados do assessment não encontrados', 'error')
            return redirect(url_for('completed_assessments'))
        
        print(f"Rendering results template with data: {results}")
        print(f"Assessment ID being passed to template: {assessment_id}")
        
        return render_template('results.html',
                             template_name=results['template_name'],
                             category_scores=results['category_scores'],
                             final_score=results['final_score'],
                             total_points=results['total_points'],
                             total_possible=results['total_possible'],
                             assessment_id=assessment_id)
                             
    except Exception as e:
        print(f"\nError showing results: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        flash('Erro ao exibir os resultados. Por favor, tente novamente.', 'error')
        return redirect(url_for('completed_assessments'))

@app.route('/completed-assessments/delete/<int:assessment_id>', methods=['DELETE'])
def delete_assessment(assessment_id):
    try:
        assessment = next((a for a in COMPLETED_ASSESSMENTS if a['id'] == assessment_id), None)
        if assessment:
            COMPLETED_ASSESSMENTS.remove(assessment)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Assessment não encontrado'})
    except Exception as e:
        print(f"Erro ao excluir assessment: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao excluir o assessment'})

def get_category_color(category):
    """Retorna uma cor consistente para cada categoria."""
    colors = {
        'Arquitetura': '#0d6efd',
        'Resiliência': '#6610f2',
        'Cyber Segurança': '#6f42c1',
        'Governança': '#d63384',
        'FinOps': '#dc3545'
    }
    return colors.get(category, '#0d6efd')

def generate_sample_completed_assessments():
    """Gera dados de exemplo para demonstração."""
    try:
        print("\n=== Generating sample assessments ===")
        start_date = datetime.now() - timedelta(days=180)
        
        COMPLETED_ASSESSMENTS.clear()
        print("Cleared existing assessments")
        
        for i in range(20):
            assessment_date = (start_date + timedelta(days=i*9)).strftime('%Y-%m-%d')
            
            # Selecionar um template
            template = TEMPLATES[i % len(TEMPLATES)]
            print(f"\nCreating assessment {i+1} using template: {template['name']}")
            
            # Inicializar estruturas
            categories = []
            category_scores = {}
            total_points = 0
            total_possible = 0
            responses = {}
            
            # Processar cada categoria do template
            print("Processing categories:")
            for category_id in template['category_ids']:
                category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
                if category:
                    print(f"- Found category: {category['name']}")
                    categories.append(category['name'])
                    
                    # Inicializar contadores da categoria
                    category_points = 0
                    category_possible = 0
                    questions_answered = 0
                    questions_not_applicable = 0
                    
                    # Gerar respostas para cada questão
                    print(f"  Processing {len(category['questions'])} questions")
                    for question in category['questions']:
                        # Gerar uma resposta aleatória
                        response_options = ['total', 'parcial', 'nao_atendida', 'nao_se_aplica']
                        response = response_options[i % len(response_options)]
                        responses[question['id']] = response
                        
                        # Calcular pontos se não for N/A
                        if response != 'nao_se_aplica':
                            weight = question.get('weight', 1)
                            multiplier = SCORING_MULTIPLIERS[response]
                            if multiplier is not None:
                                points = weight * multiplier
                                category_points += points
                                category_possible += weight
                                questions_answered += 1
                        else:
                            questions_not_applicable += 1
                    
                    # Calcular percentual da categoria
                    total_questions = len(category['questions'])
                    category_percentage = (category_points / category_possible * 100) if category_possible > 0 else 0
                    
                    # Armazenar resultados da categoria
                    category_scores[category_id] = {
                        'name': category['name'],
                        'points': category_points,
                        'total_possible': category_possible,
                        'questions_answered': questions_answered,
                        'questions_not_applicable': questions_not_applicable,
                        'total_questions': total_questions,
                        'percentage': round(category_percentage, 1)
                    }
                    
                    # Atualizar totais gerais
                    total_points += category_points
                    total_possible += category_possible
                    
                    print(f"  Category score: {category_percentage:.1f}%")
            
            # Calcular pontuação final
            final_score = round((total_points / total_possible * 100), 1) if total_possible > 0 else 0
            
            # Criar o assessment
            new_assessment = {
                'id': i + 1,
                'template_id': template['id'],
                'date': assessment_date,
                'name': template['name'],
                'categories': categories,
                'category_scores': category_scores,
                'total_points': total_points,
                'total_possible': total_possible,
                'status': 'Concluído' if i % 5 != 0 else 'Em Andamento',
                'score': final_score,
                'responses': responses
            }
            
            print(f"Created assessment:")
            print(f"- ID: {new_assessment['id']}")
            print(f"- Template: {new_assessment['name']}")
            print(f"- Categories: {len(new_assessment['categories'])}")
            print(f"- Responses: {len(new_assessment['responses'])}")
            print(f"- Final Score: {new_assessment['score']}%")
            
            COMPLETED_ASSESSMENTS.append(new_assessment)
        
        print(f"\nGenerated {len(COMPLETED_ASSESSMENTS)} sample assessments")
        
    except Exception as e:
        print("\n=== Error generating sample assessments ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

# Rotas para gerenciamento de categorias
@app.route('/manage/categories')
def manage_categories():
    return render_template('manage_categories.html', categories=CATEGORIES_DATA)

@app.route('/manage/categories/add', methods=['POST'])
def add_category():
    try:
        category_id = request.form.get('id')
        name = request.form.get('name')
        description = request.form.get('description', '')
        baseline = float(request.form.get('baseline', 70))
        
        # Validar dados
        if not category_id or not name:
            flash('ID e Nome são obrigatórios', 'danger')
            return redirect(url_for('manage_categories'))
        
        # Verificar se ID já existe
        if any(c['id'] == category_id for c in CATEGORIES_DATA):
            flash('Já existe uma categoria com este ID', 'danger')
            return redirect(url_for('manage_categories'))
        
        # Criar nova categoria
        new_category = {
            'id': category_id,
            'name': name,
            'description': description,
            'baseline': baseline,
            'questions': []
        }
        
        CATEGORIES_DATA.append(new_category)
        
        # Atualizar o baseline global
        CATEGORY_BASELINES[name] = baseline
        
        flash('Categoria criada com sucesso', 'success')
        
    except Exception as e:
        print(f"Erro ao adicionar categoria: {str(e)}")
        flash('Erro ao criar categoria', 'danger')
    
    return redirect(url_for('manage_categories'))

@app.route('/manage/categories/edit', methods=['POST'])
def edit_category():
    try:
        original_id = request.form.get('original_id')
        new_id = request.form.get('id')
        name = request.form.get('name')
        description = request.form.get('description', '')
        baseline = float(request.form.get('baseline', 70))
        
        # Validar dados
        if not new_id or not name:
            flash('ID e Nome são obrigatórios', 'danger')
            return redirect(url_for('manage_categories'))
        
        # Encontrar categoria
        category = next((c for c in CATEGORIES_DATA if c['id'] == original_id), None)
        if not category:
            flash('Categoria não encontrada', 'danger')
            return redirect(url_for('manage_categories'))
        
        # Verificar se novo ID já existe (se for diferente do original)
        if new_id != original_id and any(c['id'] == new_id for c in CATEGORIES_DATA):
            flash('Já existe uma categoria com este ID', 'danger')
            return redirect(url_for('manage_categories'))
        
        # Atualizar categoria
        old_name = category['name']  # Guardar nome antigo para atualizar CATEGORY_BASELINES
        category['id'] = new_id
        category['name'] = name
        category['description'] = description
        category['baseline'] = baseline
        
        # Atualizar o baseline global
        if old_name in CATEGORY_BASELINES:
            del CATEGORY_BASELINES[old_name]
        CATEGORY_BASELINES[name] = baseline
        
        flash('Categoria atualizada com sucesso', 'success')
        
    except Exception as e:
        print(f"Erro ao editar categoria: {str(e)}")
        flash('Erro ao atualizar categoria', 'danger')
    
    return redirect(url_for('manage_categories'))

@app.route('/api/categories/<category_id>')
def get_category(category_id):
    category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
    if category:
        return jsonify({
            'id': category['id'],
            'name': category['name'],
            'description': category.get('description', ''),
            'baseline': category.get('baseline', CATEGORY_BASELINES.get(category['name'], 70))
        })
    return jsonify({'error': 'Categoria não encontrada'}), 404

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category_api(category_id):
    try:
        # Verificar se existem assessments usando esta categoria
        assessments_with_category = [a for a in COMPLETED_ASSESSMENTS if category_id in a['categories']]
        if assessments_with_category:
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir esta categoria pois existem assessments que a utilizam.'
            })
        
        # Remover a categoria
        category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
        if category:
            CATEGORIES_DATA.remove(category)
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Categoria não encontrada'})
    except Exception as e:
        print(f"Erro ao excluir categoria: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao excluir categoria'})

# Rotas para gerenciamento de perguntas
@app.route('/manage/questions')
def manage_questions():
    # Preparar lista de questões com informações da categoria
    questions = []
    for category in CATEGORIES_DATA:
        for question in category['questions']:
            questions.append({
                'id': question['id'],
                'category_id': category['id'],
                'category_name': category['name'],
                'text': question['text'],
                'weight': question.get('weight', 1)
            })
    
    return render_template('manage_questions.html', 
                         questions=questions,
                         categories=CATEGORIES_DATA)

@app.route('/manage/questions/add', methods=['POST'])
def add_question():
    try:
        category_id = request.form.get('category_id')
        text = request.form.get('text')
        weight = int(request.form.get('weight', 1))
        recommended_actions = request.form.get('recommended_actions')
        implementation_time = request.form.get('implementation_time')
        
        # Validar dados
        if not category_id or not text:
            flash('Categoria e texto da pergunta são obrigatórios', 'danger')
            return redirect(url_for('manage_questions'))
        
        # Encontrar categoria
        category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
        if not category:
            flash('Categoria não encontrada', 'danger')
            return redirect(url_for('manage_questions'))
        
        # Gerar ID único para a questão
        question_id = f"{category_id}{len(category['questions']) + 1}"
        
        # Criar nova questão
        new_question = {
            'id': question_id,
            'text': text,
            'weight': weight,
            'recommended_actions': recommended_actions,
            'implementation_time': implementation_time
        }
        
        category['questions'].append(new_question)
        flash('Pergunta adicionada com sucesso', 'success')
        
    except Exception as e:
        print(f"Erro ao adicionar pergunta: {str(e)}")
        flash('Erro ao adicionar pergunta', 'danger')
    
    return redirect(url_for('manage_questions'))

@app.route('/manage/questions/edit', methods=['POST'])
def edit_question():
    try:
        question_id = request.form.get('question_id')
        category_id = request.form.get('category_id')
        text = request.form.get('text')
        weight = int(request.form.get('weight', 1))
        recommended_actions = request.form.get('recommended_actions')
        implementation_time = request.form.get('implementation_time')
        
        # Validar dados
        if not question_id or not category_id or not text:
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('manage_questions'))
        
        # Encontrar e remover a questão antiga
        old_category = None
        question_to_move = None
        for category in CATEGORIES_DATA:
            question = next((q for q in category['questions'] if q['id'] == question_id), None)
            if question:
                old_category = category
                question_to_move = question
                break
        
        if not question_to_move:
            flash('Pergunta não encontrada', 'danger')
            return redirect(url_for('manage_questions'))
        
        # Se mudou de categoria, mover para a nova
        new_category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
        if not new_category:
            flash('Categoria não encontrada', 'danger')
            return redirect(url_for('manage_questions'))
        
        if old_category['id'] != new_category['id']:
            old_category['questions'].remove(question_to_move)
            # Atualizar ID da questão para refletir nova categoria
            question_to_move['id'] = f"{category_id}{len(new_category['questions']) + 1}"
            new_category['questions'].append(question_to_move)
        
        # Atualizar dados da questão
        question_to_move['text'] = text
        question_to_move['weight'] = weight
        question_to_move['recommended_actions'] = recommended_actions
        question_to_move['implementation_time'] = implementation_time
        
        flash('Pergunta atualizada com sucesso', 'success')
        
    except Exception as e:
        print(f"Erro ao editar pergunta: {str(e)}")
        flash('Erro ao atualizar pergunta', 'danger')
    
    return redirect(url_for('manage_questions'))

@app.route('/api/questions/<question_id>')
def get_question(question_id):
    for category in CATEGORIES_DATA:
        question = next((q for q in category['questions'] if q['id'] == question_id), None)
        if question:
            return jsonify({
                'id': question['id'],
                'category_id': category['id'],
                'text': question['text'],
                'weight': question.get('weight', 1),
                'recommended_actions': question.get('recommended_actions', ''),
                'implementation_time': question.get('implementation_time', '')
            })
    return jsonify({'error': 'Pergunta não encontrada'}), 404

@app.route('/api/questions/<question_id>', methods=['DELETE'])
def delete_question_api(question_id):
    try:
        # Procurar e remover a questão
        for category in CATEGORIES_DATA:
            question = next((q for q in category['questions'] if q['id'] == question_id), None)
            if question:
                category['questions'].remove(question)
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Pergunta não encontrada'})
    except Exception as e:
        print(f"Erro ao excluir pergunta: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro ao excluir pergunta'})

@app.route('/assessment/<int:assessment_id>/questions')
def assessment_questions(assessment_id):
    try:
        print("\n=== Showing assessment questions ===")
        
        # Encontrar o assessment
        assessment = next((a for a in COMPLETED_ASSESSMENTS if a['id'] == assessment_id), None)
        if not assessment:
            print("Assessment not found")
            flash('Assessment não encontrado', 'error')
            return redirect(url_for('completed_assessments'))
        
        print(f"Found assessment: {assessment['name']}")
        
        # Encontrar o template
        template = next((t for t in TEMPLATES if t['id'] == assessment.get('template_id')), None)
        if not template:
            print("Template not found")
            flash('Template não encontrado', 'error')
            return redirect(url_for('completed_assessments'))
        
        print(f"Found template: {template['name']}")
        
        # Preparar dados das categorias com suas questões
        categories = []
        weights = set()  # Conjunto para armazenar pesos únicos
        
        # Garantir que temos as respostas
        responses = {}
        if 'responses' in assessment:
            responses = assessment['responses']
        else:
            # Se não temos respostas, tentar reconstruir a partir dos dados da categoria
            print("No responses found, trying to reconstruct from category scores")
            for category_id, category_data in assessment.get('category_scores', {}).items():
                category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
                if category:
                    for question in category['questions']:
                        # Determinar resposta com base na pontuação
                        if category_data.get('questions_not_applicable', 0) > 0:
                            responses[question['id']] = 'nao_se_aplica'
                        else:
                            responses[question['id']] = 'total'  # Valor padrão
        
        print(f"Responses data: {responses}")
        
        for category_id in template['category_ids']:
            category = next((c for c in CATEGORIES_DATA if c['id'] == category_id), None)
            if category:
                # Adicionar pesos únicos ao conjunto
                for question in category['questions']:
                    weights.add(question.get('weight', 1))
                    # Garantir que cada questão tenha uma resposta
                    if question['id'] not in responses:
                        responses[question['id']] = 'nao_atendida'
                
                categories.append(category)
        
        # Ordenar pesos
        weights = sorted(list(weights))
        
        print(f"Prepared data:")
        print(f"- Categories: {len(categories)}")
        print(f"- Weights: {weights}")
        print(f"- Total responses: {len(responses)}")
        
        return render_template('assessment_questions.html',
                             assessment=assessment,
                             categories=categories,
                             responses=responses,
                             weights=weights)
                             
    except Exception as e:
        print(f"\nError showing assessment questions: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar detalhes do assessment', 'error')
        return redirect(url_for('completed_assessments'))

if __name__ == '__main__':
    app.run(debug=True)
