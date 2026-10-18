from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.skill import Skill
from app.services.skill_catalog import sync_skill_id_sequence


SKILL_CATALOG = (
    ("Python", "Programming Languages", "General-purpose language widely used for backend, automation, and data work."),
    ("Java", "Programming Languages", "Object-oriented language commonly used for enterprise and Android applications."),
    ("JavaScript", "Programming Languages", "Core programming language for interactive web applications."),
    ("TypeScript", "Programming Languages", "Statically typed JavaScript for maintainable web applications."),
    ("C#", "Programming Languages", "Programming language for .NET, desktop, web, and game development."),
    ("C++", "Programming Languages", "Systems programming language for high-performance applications."),
    ("Go", "Programming Languages", "Compiled language designed for simple and scalable services."),
    ("PHP", "Programming Languages", "Server-side language used for web application development."),
    ("Kotlin", "Programming Languages", "Modern language used for Android and JVM applications."),
    ("Swift", "Programming Languages", "Programming language for iOS and macOS applications."),
    ("HTML", "Frontend", "Markup language used to structure web pages."),
    ("CSS", "Frontend", "Style sheet language used to design responsive web interfaces."),
    ("React", "Frontend", "Component-based library for building user interfaces."),
    ("Next.js", "Frontend", "React framework for full-stack, server-rendered web applications."),
    ("Vue.js", "Frontend", "Progressive framework for building web user interfaces."),
    ("Angular", "Frontend", "Framework for building large-scale web applications."),
    ("Tailwind CSS", "Frontend", "Utility-first CSS framework for rapid interface development."),
    ("Node.js", "Backend", "JavaScript runtime for APIs and server-side applications."),
    ("FastAPI", "Backend", "Python framework for fast, typed web APIs."),
    ("Django", "Backend", "Python framework for secure, full-featured web applications."),
    ("Flask", "Backend", "Lightweight Python framework for web services."),
    ("Spring Boot", "Backend", "Java framework for production-ready services and APIs."),
    ("ASP.NET Core", "Backend", "Cross-platform .NET framework for web APIs and applications."),
    ("Laravel", "Backend", "PHP framework for modern web applications."),
    ("REST API", "Backend", "Design and implementation of resource-oriented HTTP APIs."),
    ("GraphQL", "Backend", "Query language and runtime for flexible application APIs."),
    ("SQL", "Databases", "Language for querying and managing relational data."),
    ("PostgreSQL", "Databases", "Open-source relational database with advanced SQL features."),
    ("MySQL", "Databases", "Popular open-source relational database."),
    ("SQL Server", "Databases", "Microsoft relational database platform."),
    ("MongoDB", "Databases", "Document database for flexible application data."),
    ("Redis", "Databases", "In-memory data store for caching and real-time workloads."),
    ("Git", "DevOps", "Version control for collaborative software development."),
    ("Linux", "DevOps", "Administration and development on Linux-based systems."),
    ("Docker", "DevOps", "Container platform for packaging and running applications."),
    ("Kubernetes", "DevOps", "Platform for deploying and managing containerized workloads."),
    ("CI/CD", "DevOps", "Automated software build, test, and delivery practices."),
    ("AWS", "Cloud", "Amazon cloud services for computing, storage, and deployment."),
    ("Microsoft Azure", "Cloud", "Microsoft cloud platform for applications and infrastructure."),
    ("Google Cloud", "Cloud", "Google cloud platform for applications, data, and AI."),
    ("Data Analysis", "Data & AI", "Inspecting and interpreting data to support decisions."),
    ("Pandas", "Data & AI", "Python library for tabular data analysis."),
    ("NumPy", "Data & AI", "Python library for numerical computing."),
    ("Machine Learning", "Data & AI", "Building predictive systems that learn from data."),
    ("Deep Learning", "Data & AI", "Developing neural-network-based AI solutions."),
    ("TensorFlow", "Data & AI", "Framework for developing and deploying machine learning models."),
    ("PyTorch", "Data & AI", "Framework for deep learning research and production."),
    ("Power BI", "Data & AI", "Business intelligence dashboards and data visualization."),
    ("Unit Testing", "Quality Assurance", "Writing automated tests for individual units of code."),
    ("Pytest", "Quality Assurance", "Python framework for readable automated tests."),
    ("Jest", "Quality Assurance", "JavaScript and TypeScript testing framework."),
    ("Selenium", "Quality Assurance", "Browser automation for end-to-end web testing."),
    ("Figma", "Design", "Collaborative interface design and prototyping tool."),
    ("UI/UX Design", "Design", "Designing usable, accessible, and engaging product experiences."),
    ("Agile", "Ways of Working", "Iterative product delivery and continuous improvement practices."),
    ("Scrum", "Ways of Working", "Agile framework for planning and delivering work in sprints."),
    ("Communication", "Soft Skills", "Sharing information clearly with teammates and stakeholders."),
    ("Teamwork", "Soft Skills", "Collaborating effectively toward shared goals."),
    ("Problem Solving", "Soft Skills", "Analyzing challenges and producing practical solutions."),
    ("Time Management", "Soft Skills", "Prioritizing work and meeting commitments efficiently."),
    ("English", "Languages", "Professional written and spoken English communication."),
    ("C", "Programming Languages", "Procedural language widely used for systems and embedded software."),
    ("Dart", "Programming Languages", "Programming language used with Flutter for cross-platform applications."),
    ("Ruby", "Programming Languages", "Dynamic language commonly used for web application development."),
    ("Rust", "Programming Languages", "Memory-safe systems language for reliable high-performance software."),
    ("Scala", "Programming Languages", "JVM language combining object-oriented and functional programming."),
    ("Bootstrap", "Frontend", "Component toolkit for responsive web interfaces."),
    ("Sass", "Frontend", "CSS preprocessor for maintainable and reusable styles."),
    ("Redux", "Frontend", "Predictable state management for JavaScript applications."),
    ("React Native", "Mobile", "React framework for native mobile applications."),
    ("React Query", "Frontend", "Server-state fetching and caching for React applications."),
    ("Express.js", "Backend", "Minimal Node.js framework for APIs and web services."),
    ("NestJS", "Backend", "Structured Node.js framework for scalable server applications."),
    ("Ruby on Rails", "Backend", "Full-stack Ruby framework for web applications."),
    ("MariaDB", "Databases", "Open-source relational database compatible with MySQL."),
    ("Oracle Database", "Databases", "Enterprise relational database management system."),
    ("SQLite", "Databases", "Embedded relational database for local application storage."),
    ("Neo4j", "Databases", "Graph database for highly connected data."),
    ("Firebase", "Cloud", "Managed platform for application data, authentication, and hosting."),
    ("GitHub", "DevOps", "Collaborative Git hosting and software delivery platform."),
    ("GitHub Actions", "DevOps", "GitHub-native workflow automation and CI/CD."),
    ("GitLab", "DevOps", "Git repository and integrated DevOps platform."),
    ("Nginx", "DevOps", "Web server, reverse proxy, and load balancer."),
    ("Terraform", "DevOps", "Infrastructure-as-code tool for repeatable cloud provisioning."),
    ("Jenkins", "DevOps", "Automation server for continuous integration and delivery."),
    ("Natural Language Processing", "Data & AI", "Techniques for understanding and generating human language."),
    ("Computer Vision", "Data & AI", "Techniques for interpreting images and video."),
    ("Scikit-learn", "Data & AI", "Python library for practical machine learning."),
    ("YOLO", "Data & AI", "Real-time object detection model family."),
    ("RAG", "Data & AI", "Retrieval-augmented generation for grounded AI responses."),
    ("LangChain", "Data & AI", "Framework for applications powered by language models."),
    ("Apache Spark", "Data & AI", "Distributed engine for large-scale data processing."),
    ("Microservices", "Software Engineering", "Designing systems as independently deployable services."),
    ("Object-Oriented Programming", "Software Engineering", "Software design using objects, classes, and encapsulation."),
    ("Design Patterns", "Software Engineering", "Reusable solutions to common software design problems."),
    ("System Design", "Software Engineering", "Designing scalable and reliable software architectures."),
    ("Postman", "Tools", "API development, testing, and collaboration tool."),
    ("Jira", "Tools", "Issue tracking and agile project management tool."),
    ("Visual Studio Code", "Tools", "Extensible source code editor for software development."),
    ("Leadership", "Soft Skills", "Guiding teams and taking ownership of shared outcomes."),
    ("Critical Thinking", "Soft Skills", "Evaluating information and making reasoned decisions."),
    ("Adaptability", "Soft Skills", "Responding effectively to changing requirements and environments."),
)


def seed_skill_catalog(db: Session) -> int:
    """Insert missing catalog entries without changing existing skills."""
    existing_names = {
        skill_name.casefold()
        for (skill_name,) in db.query(Skill.skill_name).all()
    }
    missing_skills = [
        Skill(skill_name=name, category=category, description=description)
        for name, category, description in SKILL_CATALOG
        if name.casefold() not in existing_names
    ]

    if missing_skills:
        sync_skill_id_sequence(db)
        db.add_all(missing_skills)
        db.commit()

    return len(missing_skills)


def main() -> None:
    with SessionLocal() as db:
        added_count = seed_skill_catalog(db)
    print(f"Skill catalog ready: {added_count} new skills added.")


if __name__ == "__main__":
    main()
