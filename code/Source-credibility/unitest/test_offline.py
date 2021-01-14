from services.services import SourceCredibilityService

source_credibility_service: SourceCredibilityService = SourceCredibilityService()
output_offline = source_credibility_service.offline_service()
