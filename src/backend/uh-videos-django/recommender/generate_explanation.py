from .models import Rating, User

def generate_explanation(trace, recommended_movie_idx, movies, user_id, collaborative_scores, content_scores):
    """
    Genera una explicación en lenguaje natural sobre por qué se recomendó una película,
    destacando el enfoque predominante (colaborativo o basado en contenido).

    Parámetros:
    - trace (dict): Un diccionario que contiene las trazas de ambos enfoques.
    - recommended_movie_idx (int): El índice de la película recomendada.
    - movies (QuerySet): El conjunto de películas disponibles.
    - user_id (int): El ID del usuario para el cual se genera la explicación.
    - collaborative_scores (np.ndarray): Las calificaciones basadas en filtrado colaborativo.
    - content_scores (np.ndarray): Las calificaciones basadas en contenido.

    Retorna:
    - str: Una explicación en lenguaje natural sobre por qué se recomendó la película.
    """
    # Determinar qué enfoque tuvo más peso
    collaborative_score = collaborative_scores[recommended_movie_idx]
    content_score = content_scores[recommended_movie_idx]

    if collaborative_score > content_score * 1.2:  # Si el enfoque colaborativo tiene significativamente más peso
        return collaborative_explanation(trace, user_id)
    elif content_score > collaborative_score * 1.2:  # Si el enfoque basado en contenido tiene significativamente más peso
        return content_based_explanation(trace, recommended_movie_idx, movies, user_id)
    else:  # Si ambos enfoques tienen peso similar, usar una explicación combinada
        return combined_explanation(trace, user_id)

def collaborative_explanation(trace, user_id):
    """
    Genera una explicación basada en la similitud de usuarios, utilizando los IDs reales de los usuarios
    y organizándolos según su similitud.

    Parámetros:
    - trace (dict): Un diccionario que contiene las puntuaciones de similitud del usuario y las calificaciones ponderadas.
    - user_id (int): El ID del usuario para el cual se genera la explicación.

    Retorna:
    - str: Una explicación en lenguaje natural sobre por qué se recomienda una película.
    """
    # Obtener los IDs de los usuarios y sus correspondientes similitudes
    user_similarity_scores = trace['collaborative_filtering']['user_similarity_scores']
    users = User.objects.all()

    # Crear una lista de tuplas (user_id, similarity) excluyendo al usuario actual
    similar_users = [(user.id, score) for user, score in zip(users, user_similarity_scores) if score > 0.7 and user.id != user_id]

    # Ordenar la lista de tuplas por similitud en orden descendente
    similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)

    # Extraer solo los IDs de los usuarios ordenados por similitud
    similar_user_ids = [user_id for user_id, _ in similar_users]

    # Generar la explicación en lenguaje natural
    if similar_user_ids:
        return f"Te recomendamos esta película porque los usuarios con ids:{similar_user_ids} vieron películas similares a las tuyas y la calificaron bien."
    return "Te recomendamos esta película basada en las preferencias de usuarios similares a ti."

def content_based_explanation(trace, recommended_movie_idx, movies, user_id):
    """
    Genera una explicación basada en el filtrado basado en contenido, identificando las características de las películas
    que son similares a las que el usuario ya ha calificado positivamente.

    Parámetros:
    - trace (dict): Un diccionario que contiene las características y calificaciones basadas en contenido.
    - recommended_movie_idx (int): El índice de la película recomendada.
    - movies (QuerySet): El conjunto de películas disponibles.
    - user_id (int): El ID del usuario para el cual se genera la explicación.

    Retorna:
    - str: Una explicación en lenguaje natural sobre por qué se recomienda una película.
    """
    seen_movies = Rating.objects.filter(user_id=user_id).values_list('movie__title', flat=True)
    similar_movies = []
    characteristics = set()  # Usar un conjunto para evitar duplicados
    for idx, score in enumerate(trace['content_based_filtering']['content_scores']):
        if idx != recommended_movie_idx and score > 0.5 and movies[idx].title not in seen_movies:
            similar_movies.append(movies[idx].title)
            if 'genre' in trace['content_based_filtering']['content_based_features'][idx]:
                characteristics.add('género')
            if 'director' in trace['content_based_filtering']['content_based_features'][idx]:
                characteristics.add('director')

    if similar_movies and characteristics:
        return f"Esta película es similar a otras que te han gustado como {similar_movies} en cuanto al {', '.join(characteristics)}."
    return "Esta película se basa en tus preferencias pasadas."

def combined_explanation(trace, user_id):
    """
    Genera una explicación combinada cuando los enfoques colaborativo y basado en contenido tienen pesos similares
    en la recomendación de una película.

    Parámetros:
    - trace (dict): Un diccionario que contiene las trazas de ambos enfoques.
    - user_id (int): El ID del usuario para el cual se genera la explicación.

    Retorna:
    - str: Una explicación en lenguaje natural sobre por qué se recomienda una película.
    """
    similar_users = [user.id for user in User.objects.all() if trace['collaborative_filtering']['user_similarity_scores'][list(User.objects.all()).index(user)] > 0.3 and user.id != user_id]
    if similar_users:
        return f"Esta recomendación se basa en tus calificaciones anteriores y en la similitud con los gustos de otros usuarios similares como {similar_users}."
    return "Esta recomendación se basa en tus calificaciones anteriores."
