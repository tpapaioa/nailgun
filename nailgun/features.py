"""Feature availability registry for nailgun based on Satellite version.

Similar to airgun.features but for API-level features.
"""

from packaging.version import Version


class FeatureDefinition:
    """Definition of a feature and its version-specific availability.

    Attributes:
        name: Unique identifier
        min_version: Minimum Satellite version (inclusive, None = all versions before max_version)
        max_version: Maximum Satellite version (inclusive, None = all versions after min_version)
        description: Human-readable description
        replacement: Name of feature that replaces this feature in later versions (optional)

    Example - Feature removed in 6.19:
        FeatureDefinition(
            name='activation_key.auto_attach',
            max_version='6.18',
            description='Auto-attach functionality',
        )

    """

    def __init__(
        self,
        name,
        min_version=None,
        max_version=None,
        description='',
        replacement=None,
    ):
        self.name = name
        self.min_version = min_version
        self.max_version = max_version
        self.description = description
        self.replacement = replacement if replacement is not None else ''


FEATURE_DEFS = [
    # ActivationKey API features
    FeatureDefinition(
        name='api.activation_key.auto_attach',
        max_version='6.18',
        description='Auto-attach subscriptions field',
    ),
    FeatureDefinition(
        name='api.activation_key.content_view',
        max_version='6.19',
        description='Single content_view/environment fields',
    ),
    # HostSubscription API features
    FeatureDefinition(
        name='api.host_subscription.entity',
        max_version='6.18',
        description='HostSubscription entity',
    ),
    # ContentView API features
    FeatureDefinition(
        name='api.content_view.rolling',
        min_version='6.18',
        description='Rolling content views field',
    ),
    # Repository API features
    FeatureDefinition(
        name='api.repository.download_concurrency',
        min_version='6.18',
        description='Download concurrency field for repository sync',
    ),
]

FEATURE_MATRIX = {fd.name: fd for fd in FEATURE_DEFS}


class VersionFeatureChecker:
    """Check feature availability for a specific Satellite version.

    Instantiate with a Satellite version, then query features with has_feature().
    """

    def __init__(self, satellite_version):
        """Initialize checker with Satellite version.

        Args:
            satellite_version: Satellite version string (e.g., '6.18.0', '6.19')

        """
        self.satellite_version = satellite_version

    def version_match(self, min_version=None, max_version=None):
        """Check whether the given Satellite version falls between the given
        (min_version, max_version) range. The endpoints are inclusive, including
        .z versions.

        For example,
        version='6.18.6', min_version='6.17', max_version='6.18' returns True
        version='6.18', min_version='6.18', max_version='6.19' returns True
        """
        version_obj = self.satellite_version if isinstance(self.satellite_version, Version) else Version(self.satellite_version)

        next_version = None
        if max_version:
            v = Version(max_version)
            next_version = f"{v.major}.{v.minor + 1}"

        return not (
            (min_version and version_obj < Version(min_version))
            or (next_version and version_obj >= Version(next_version))
        )

    def has_feature(self, feature_name):
        """Check if feature is available in this Satellite version.

        Args:
            feature_name: Name of the feature

        Returns:
            True if feature is available

        """
        if not (feature := FEATURE_MATRIX.get(feature_name)):
            # Unknown features are assumed unavailable
            return False

        return self.version_match(min_version=feature.min_version, max_version=feature.max_version)
