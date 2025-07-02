import os
from flask import flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Dados hardcoded para demonstração
CATEGORIES_DATA = {
    'arquitetura': {
        'id': 'arquitetura',
        'name': 'Arquitetura',
        'description': 'Avaliação da arquitetura cloud',
        'baseline': 75,
        'questions': [
            {
                'id': 'arq_001',
                'text': 'A arquitetura segue os princípios de Well-Architected Framework?',
                'weight': 5,
                'category_id': 'arquitetura',
                'recommended_actions': 'Implementar os 5 pilares do Well-Architected Framework\nRealizar revisão arquitetural\nDocumentar decisões arquiteturais',
                'implementation_time': '3_months'
            },
            {
                'id': 'arq_002',
                'text': 'Os componentes são fracamente acoplados e altamente coesos?',
                'weight': 4,
                'category_id': 'arquitetura',
                'recommended_actions': 'Refatorar componentes monolíticos\nImplementar padrões de microserviços\nUsar APIs bem definidas',
                'implementation_time': '6_months'
            },
            {
                'id': 'arq_003',
                'text': 'A arquitetura suporta escalabilidade horizontal?',
                'weight': 4,
                'category_id': 'arquitetura',
                'recommended_actions': 'Implementar auto-scaling\nUsar load balancers\nOtimizar para stateless',
                'implementation_time': '2_months'
            }
        ]
    },
    'resiliencia': {
        'id': 'resiliencia',
        'name': 'Resiliência',
        'description': 'Avaliação da resiliência e disponibilidade',
        'baseline': 80,
        'questions': [
            {
                'id': 'res_001',
                'text': 'Existem mecanismos de backup e recovery implementados?',
                'weight': 5,
                'category_id': 'resiliencia',
                'recommended_actions': 'Implementar backup automatizado\nTestar procedimentos de recovery\nDocumentar RTO e RPO',
                'implementation_time': '1_month'
            },
            {
                'id': 'res_002',
                'text': 'A aplicação possui circuit breakers e retry policies?',
                'weight': 4,
                'category_id': 'resiliencia',
                'recommended_actions': 'Implementar circuit breakers\nConfigurar retry policies\nMonitorar falhas de dependências',
                'implementation_time': '2_weeks'
            }
        ]
    },
    'seguranca': {
        'id': 'seguranca',
        'name': 'Cyber Segurança',
        'description': 'Avaliação de segurança',
        'baseline': 85,
        'questions': [
            {
                'id': 'seg_001',
                'text': 'Todos os dados em trânsito e em repouso estão criptografados?',
                'weight': 5,
                'category_id': 'seguranca',
                'recommended_actions': 'Implementar TLS 1.3\nCriptografar dados em repouso\nGerenciar chaves de criptografia',
                'implementation_time': '1_month'
            },
            {
                'id': 'seg_002',
                'text': 'Existe controle de acesso baseado em roles (RBAC)?',
                'weight': 4,
                'category_id': 'seguranca',
                'recommended_actions': 'Implementar RBAC\nConfigurar IAM policies\nRealizar auditoria de acessos',
                'implementation_time': '2_months'
            }
        ]
    },
    'governanca': {
        'id': 'governanca',
        'name': 'Governança',
        'description': 'Avaliação de governança e compliance',
        'baseline': 70,
        'questions': [
            {
                'id': 'gov_001',
                'text': 'Existem políticas de governança documentadas e implementadas?',
                'weight': 4,
                'category_id': 'governanca',
                'recommended_actions': 'Documentar políticas de governança\nImplementar controles de compliance\nRealizar auditorias regulares',
                'implementation_time': '3_months'
            }
        ]
    },
    'finops': {
        'id': 'finops',
        'name': 'FinOps',
        'description': 'Avaliação de otimização financeira',
        'baseline': 65,
        'questions': [
            {
                'id': 'fin_001',
                'text': 'Existe monitoramento e otimização contínua de custos?',
                'weight': 5,
                'category_id': 'finops',
                'recommended_actions': 'Implementar cost monitoring\nOtimizar recursos ociosos\nUsar reserved instances',
                'implementation_time': '1_month'
            }
        ]
    }
}

# Simulação de banco de dados em memória
templates_db = []
assessments_db = []
next_template_id = 1
next_assessment_id = 1

@app.route('/')
def index():
    # Calcular métricas para o dashboard
    total_assessments = len(templates_db)
    completed_assessments = len([a for a in assessments_db if a.get('status') == 'concluido'])
    
    # Calcular média de pontuação
    completed_scores = [a.get('score', 0) for a in assessments_db if a.get('status') == 'concluido' and a.get('score') is not None]
    avg_score = round(sum(completed_scores) / len(completed_scores)) if completed_scores else None
    
    # Dados para gráficos
    categories = list(CATEGORIES_DATA.keys())
    category_scores = [75, 80, 85, 70, 65]  # Dados simulados
    category_baselines = [CATEGORIES_DATA[cat]['baseline'] for cat in categories]
    category_counts = [3, 2, 2, 1, 1]  # Número de questões por categoria
    
    # Dados de tendência (simulados)
    trend_dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    trend_datasets = [
        {
            'label': 'Arquitetura',
            'data': [70, 72, 74, 75, 77],
            'borderColor': '#0d6efd',
            'tension': 0.4,
            'fill': False
        },
        {
            'label': 'Segurança',
            'data': [80, 82, 83, 85, 87],
            'borderColor': '#dc3545',
            'tension': 0.4,
            'fill': False
        }
    ]
    
    return render_template('index.html',
                         total_assessments=total_assessments,
                         completed_assessments=completed_assessments,
                         avg_score=avg_score,
                         categories=[CATEGORIES_DATA[cat]['name'] for cat in categories],
                         category_scores=category_scores,
                         category_baselines=category_baselines,
                         category_counts=category_counts,
                         trend_dates=trend_dates,
                         trend_datasets=trend_datasets)

@app.route('/templates')
def list_templates():
    categories = list(CATEGORIES_DATA.values())
    return render_template('list_templates.html', templates=templates_db, categories=categories)

@app.route('/templates/create', methods=['POST'])
def create_template():
    global next_template_id
    try:
        data = request.get_json()
        
        template = {
            'id': next_template_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'categories': [cat['name'] for cat in data['selectedCategories']],
            'category_ids': [cat['id'] for cat in data['selectedCategories']],
            'total_questions': sum(len(CATEGORIES_DATA[cat_id]['questions']) for cat_id in [cat['id'] for cat in data['selectedCategories']] if cat_id in CATEGORIES_DATA),
            'created_at': datetime.now().isoformat()
        }
        
        templates_db.append(template)
        next_template_id += 1
        
        return jsonify({'success': True, 'template': template})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/templates/<int:template_id>/delete', methods=['DELETE'])
def delete_template(template_id):
    global templates_db
    templates_db = [t for t in templates_db if t['id'] != template_id]
    return jsonify({'success': True})

@app.route('/assessment/<int:template_id>')
def start_assessment(template_id):
    template = next((t for t in templates_db if t['id'] == template_id), None)
    if not template:
        flash('Template não encontrado', 'error')
        return redirect(url_for('list_templates'))
    
    # Preparar dados das categorias e questões
    categories_data = []
    for cat_id in template['category_ids']:
        if cat_id in CATEGORIES_DATA:
            categories_data.append(CATEGORIES_DATA[cat_id])
    
    template_with_categories = {
        'id': template['id'],
        'name': template['name'],
        'categories': categories_data
    }
    
    return render_template('form.html', 
                         categories=[template_with_categories],
                         assessment_id=None,
                         saved_responses={})

@app.route('/assessment/submit', methods=['POST'])
def submit_assessment():
    global next_assessment_id
    try:
        template_id = int(request.form.get('template_id'))
        template = next((t for t in templates_db if t['id'] == template_id), None)
        
        if not template:
            flash('Template não encontrado', 'error')
            return redirect(url_for('list_templates'))
        
        # Coletar respostas
        responses = {}
        for cat_id in template['category_ids']:
            if cat_id in CATEGORIES_DATA:
                for question in CATEGORIES_DATA[cat_id]['questions']:
                    response = request.form.get(question['id'])
                    if response:
                        responses[question['id']] = response
        
        # Calcular pontuações
        category_scores = {}
        total_points = 0
        total_possible = 0
        
        for cat_id in template['category_ids']:
            if cat_id not in CATEGORIES_DATA:
                continue
                
            category = CATEGORIES_DATA[cat_id]
            cat_points = 0
            cat_possible = 0
            questions_answered = 0
            questions_not_applicable = 0
            
            for question in category['questions']:
                response = responses.get(question['id'])
                weight = question['weight']
                
                if response == 'nao_se_aplica':
                    questions_not_applicable += 1
                    continue
                elif response == 'total':
                    cat_points += weight * 100
                    questions_answered += 1
                elif response == 'parcial':
                    cat_points += weight * 50
                    questions_answered += 1
                elif response == 'nao_atendida':
                    questions_answered += 1
                
                cat_possible += weight * 100
            
            # Calcular porcentagem da categoria
            if cat_possible > 0:
                cat_percentage = round((cat_points / cat_possible) * 100)
            else:
                cat_percentage = None
            
            category_scores[cat_id] = {
                'name': category['name'],
                'points': cat_points,
                'total_possible': cat_possible,
                'percentage': cat_percentage,
                'questions_answered': questions_answered,
                'questions_not_applicable': questions_not_applicable,
                'total_questions': len(category['questions'])
            }
            
            if cat_possible > 0:  # Só incluir no total se a categoria for aplicável
                total_points += cat_points
                total_possible += cat_possible
        
        # Calcular pontuação final
        final_score = round((total_points / total_possible) * 100) if total_possible > 0 else 0
        
        # Salvar assessment
        assessment = {
            'id': next_assessment_id,
            'template_id': template_id,
            'template_name': template['name'],
            'responses': responses,
            'category_scores': category_scores,
            'final_score': final_score,
            'total_points': total_points,
            'total_possible': total_possible,
            'status': 'concluido',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'score': final_score
        }
        
        assessments_db.append(assessment)
        next_assessment_id += 1
        
        # Armazenar na sessão para exibir resultados
        session['last_assessment'] = assessment
        
        return redirect(url_for('show_results', assessment_id=assessment['id']))
        
    except Exception as e:
        flash(f'Erro ao processar assessment: {str(e)}', 'error')
        return redirect(url_for('list_templates'))

@app.route('/results/<int:assessment_id>')
def show_results(assessment_id):
    assessment = next((a for a in assessments_db if a['id'] == assessment_id), None)
    
    if not assessment:
        # Tentar pegar da sessão como fallback
        assessment = session.get('last_assessment')
        if not assessment:
            flash('Assessment não encontrado', 'error')
            return redirect(url_for('list_templates'))
    
    return render_template('results.html',
                         template_name=assessment['template_name'],
                         final_score=assessment['final_score'],
                         total_points=assessment['total_points'],
                         total_possible=assessment['total_possible'],
                         category_scores=assessment['category_scores'],
                         assessment_id=assessment['id'])

@app.route('/completed-assessments')
def completed_assessments():
    # Simular dados de assessments realizados
    completed = []
    for assessment in assessments_db:
        completed.append({
            'id': assessment['id'],
            'name': assessment['template_name'],
            'date': assessment['date'],
            'score': assessment['score'],
            'status': 'Concluído',
            'categories': ['Arquitetura', 'Segurança']  # Simplificado
        })
    
    return render_template('completed_assessments.html', completed_assessments=completed)

@app.route('/categories')
def manage_categories():
    categories = list(CATEGORIES_DATA.values())
    return render_template('manage_categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
def add_category():
    try:
        category_id = request.form.get('id')
        name = request.form.get('name')
        description = request.form.get('description', '')
        baseline = int(request.form.get('baseline', 70))
        
        if category_id in CATEGORIES_DATA:
            flash('ID da categoria já existe', 'error')
            return redirect(url_for('manage_categories'))
        
        CATEGORIES_DATA[category_id] = {
            'id': category_id,
            'name': name,
            'description': description,
            'baseline': baseline,
            'questions': []
        }
        
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('manage_categories'))
    except Exception as e:
        flash(f'Erro ao criar categoria: {str(e)}', 'error')
        return redirect(url_for('manage_categories'))

@app.route('/questions')
def manage_questions():
    categories = list(CATEGORIES_DATA.values())
    questions = []
    
    for category in categories:
        for question in category['questions']:
            question_with_category = question.copy()
            question_with_category['category_name'] = category['name']
            questions.append(question_with_category)
    
    return render_template('manage_questions.html', categories=categories, questions=questions)

@app.route('/questions/add', methods=['POST'])
def add_question():
    try:
        category_id = request.form.get('category_id')
        text = request.form.get('text')
        weight = int(request.form.get('weight', 1))
        recommended_actions = request.form.get('recommended_actions', '')
        implementation_time = request.form.get('implementation_time', '')
        
        if category_id not in CATEGORIES_DATA:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('manage_questions'))
        
        # Gerar ID único para a questão
        question_id = f"{category_id}_{len(CATEGORIES_DATA[category_id]['questions']) + 1:03d}"
        
        question = {
            'id': question_id,
            'text': text,
            'weight': weight,
            'category_id': category_id,
            'recommended_actions': recommended_actions,
            'implementation_time': implementation_time
        }
        
        CATEGORIES_DATA[category_id]['questions'].append(question)
        
        flash('Pergunta criada com sucesso!', 'success')
        return redirect(url_for('manage_questions'))
    except Exception as e:
        flash(f'Erro ao criar pergunta: {str(e)}', 'error')
        return redirect(url_for('manage_questions'))

@app.route('/save-progress', methods=['POST'])
def save_progress():
    try:
        # Implementação básica para salvar progresso
        return jsonify({'success': True, 'message': 'Progresso salvo com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Rotas de API para AJAX
@app.route('/api/categories/<category_id>')
def get_category(category_id):
    if category_id in CATEGORIES_DATA:
        return jsonify(CATEGORIES_DATA[category_id])
    return jsonify({'error': 'Categoria não encontrada'}), 404

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category_api(category_id):
    if category_id in CATEGORIES_DATA:
        del CATEGORIES_DATA[category_id]
        return jsonify({'success': True})
    return jsonify({'error': 'Categoria não encontrada'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)