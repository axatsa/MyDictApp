"""
Initial seed — 20 words so the app works immediately after deploy.
Run: python seed.py
"""
import json
from database import init_db, get_word_count, insert_words

SEED_WORDS = [
    {"en": "algorithm", "uz": "algoritm", "kr": "알고리즘", "ru_def": "Набор правил для решения задачи.", "ex": ["The algorithm sorts the list in O(n log n) time.", "She designed a new algorithm for image compression.", "This algorithm predicts user behavior.", "The sorting algorithm was efficient.", "He explained the algorithm step by step."], "topic": "IT"},
    {"en": "bandwidth", "uz": "o'tkazish qobiliyati", "kr": "대역폭", "ru_def": "Максимальный объём данных за единицу времени.", "ex": ["High bandwidth is required for video streaming.", "The network bandwidth was insufficient.", "They upgraded the bandwidth to 1 Gbps.", "Bandwidth limits your download speed.", "Cloud services consume a lot of bandwidth."], "topic": "IT"},
    {"en": "eloquent", "uz": "notiq", "kr": "웅변적인", "ru_def": "Выразительно и убедительно говорящий.", "ex": ["She gave an eloquent speech.", "His eloquent words moved the audience.", "The lawyer was known for his eloquent arguments.", "An eloquent writer can change minds.", "He was eloquent and persuasive."], "topic": "Daily"},
    {"en": "resilience", "uz": "chidamlilik", "kr": "탄력성", "ru_def": "Способность восстанавливаться после трудностей.", "ex": ["Resilience is key to surviving hard times.", "She showed great resilience after the setback.", "The team's resilience was admirable.", "Mental resilience helps in stressful jobs.", "Building resilience takes practice."], "topic": "Daily"},
    {"en": "deploy", "uz": "joylashtirish", "kr": "배포", "ru_def": "Развернуть приложение или систему.", "ex": ["We will deploy the update tonight.", "The team deployed the new feature.", "Deploy the container with Docker.", "She learned to deploy apps on Linux.", "The release was deployed to production."], "topic": "IT"},
    {"en": "iterate", "uz": "takrorlash", "kr": "반복하다", "ru_def": "Повторять процесс для улучшения результата.", "ex": ["We iterate over the list of items.", "The team will iterate on the design.", "Iterate quickly and get feedback.", "Good developers iterate on their code.", "We need to iterate to find the best solution."], "topic": "IT"},
    {"en": "negotiate", "uz": "muzokaralar olib borish", "kr": "협상하다", "ru_def": "Обсуждать условия для достижения соглашения.", "ex": ["They negotiated a better salary.", "He learned to negotiate contracts.", "Negotiating is a valuable skill.", "She negotiated a deal with the client.", "The two sides agreed to negotiate."], "topic": "Business"},
    {"en": "leverage", "uz": "ta'sir kuchi", "kr": "영향력", "ru_def": "Использовать что-либо для получения преимущества.", "ex": ["Leverage your skills to find a better job.", "They leveraged data to improve decisions.", "Use your network as leverage.", "The company leveraged new technology.", "She leveraged her experience well."], "topic": "Business"},
    {"en": "hypothesis", "uz": "gipoteza", "kr": "가설", "ru_def": "Предположение, требующее проверки.", "ex": ["The scientist tested her hypothesis.", "His hypothesis was proven correct.", "Form a hypothesis before experimenting.", "The hypothesis was rejected.", "A good hypothesis is testable."], "topic": "Science"},
    {"en": "ambiguous", "uz": "noaniq", "kr": "모호한", "ru_def": "Имеющий более одного возможного значения.", "ex": ["The instructions were ambiguous.", "His answer was deliberately ambiguous.", "Ambiguous code is hard to maintain.", "The contract contained an ambiguous clause.", "She avoided ambiguous language."], "topic": "Daily"},
    {"en": "scalable", "uz": "kengaytiriladigan", "kr": "확장 가능한", "ru_def": "Способный расти без потери производительности.", "ex": ["The system is scalable to millions of users.", "Build scalable architecture from the start.", "Scalable solutions save money long-term.", "The app needs to be scalable.", "Cloud platforms are highly scalable."], "topic": "IT"},
    {"en": "intuitive", "uz": "intuitiv", "kr": "직관적인", "ru_def": "Понятный без объяснений.", "ex": ["The interface is very intuitive.", "She has an intuitive understanding of design.", "Make the app intuitive for new users.", "An intuitive UI reduces support tickets.", "The controls are intuitive and simple."], "topic": "IT"},
    {"en": "persist", "uz": "davom ettirish", "kr": "지속하다", "ru_def": "Продолжать существовать или действовать.", "ex": ["Data must persist after restart.", "She persisted despite many failures.", "Persist your settings in a config file.", "The error persisted for three days.", "Good habits persist with practice."], "topic": "IT"},
    {"en": "collaborate", "uz": "hamkorlik qilish", "kr": "협업하다", "ru_def": "Работать совместно для достижения цели.", "ex": ["The two teams collaborated on the project.", "Collaborate with your peers for better results.", "They collaborated remotely using Slack.", "Collaboration is essential in startups.", "She loves to collaborate with creative people."], "topic": "Business"},
    {"en": "optimize", "uz": "optimallashtirish", "kr": "최적화하다", "ru_def": "Улучшить эффективность системы или процесса.", "ex": ["Optimize your database queries.", "She spent hours optimizing the code.", "Optimize the image size for faster loading.", "The team optimized the checkout flow.", "Always optimize for the user experience."], "topic": "IT"},
    {"en": "streamline", "uz": "soddalashtirish", "kr": "간소화하다", "ru_def": "Упростить процесс для повышения эффективности.", "ex": ["Streamline your workflow with automation.", "The update streamlines the checkout process.", "We need to streamline our operations.", "Streamlined code is easier to maintain.", "She streamlined the onboarding experience."], "topic": "Business"},
    {"en": "vulnerable", "uz": "zaif", "kr": "취약한", "ru_def": "Подверженный атаке или вреду.", "ex": ["The system was vulnerable to SQL injection.", "Vulnerable code must be patched immediately.", "Children are the most vulnerable group.", "Never leave your server vulnerable.", "She felt vulnerable after the incident."], "topic": "IT"},
    {"en": "benchmark", "uz": "etalon", "kr": "벤치마크", "ru_def": "Стандарт для измерения производительности.", "ex": ["Run a benchmark before and after optimization.", "The new chip set a performance benchmark.", "Industry benchmarks guide our goals.", "She benchmarked the two frameworks.", "Use benchmarks to compare databases."], "topic": "IT"},
    {"en": "migrate", "uz": "ko'chirish", "kr": "마이그레이션하다", "ru_def": "Перенести данные или систему в новую среду.", "ex": ["We need to migrate the database to PostgreSQL.", "They migrated the app to the cloud.", "Migration took three days.", "Always backup before you migrate.", "She migrated the users to the new system."], "topic": "IT"},
    {"en": "momentum", "uz": "tezlanish", "kr": "모멘텀", "ru_def": "Сила или скорость движения.", "ex": ["The startup gained momentum quickly.", "Keep the momentum going.", "Losing momentum is costly in business.", "The project had great momentum.", "She used her momentum to close the deal."], "topic": "Business"},
]


if __name__ == "__main__":
    init_db()
    existing = get_word_count()
    if existing > 0:
        print(f"DB already has {existing} words. Skipping seed.")
    else:
        inserted = insert_words(SEED_WORDS)
        print(f"Seeded {inserted} words.")
