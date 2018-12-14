"""
Cyclomatic complexity metric for each function/method.

Provided by the radon library.
"""
import statistics

import radon
import radon.cli.harvest as harvesters
from radon.cli import Config
from radon.visitors import Function, Class

from wily import logger
from wily.operators import BaseOperator, Metric, MetricType


class CyclomaticComplexityOperator(BaseOperator):
    """Cyclomatic complexity operator."""

    name = "cyclomatic"
    defaults = {
        "exclude": None,
        "ignore": None,
        "min": "A",
        "max": "F",
        "no_assert": True,
        "show_closures": False,
        "order": radon.complexity.SCORE,
    }

    metrics = (
        Metric(
            "complexity",
            "Cyclomatic Complexity",
            float,
            MetricType.AimLow,
            statistics.mean,
        ),
    )

    default_metric_index = 0  # MI

    def __init__(self, config):
        """
        Instantiate a new Cyclomatic Complexity operator.

        :param config: The wily configuration.
        :type  config: :class:`WilyConfig`
        """
        # TODO: Import config for harvester from .wily.cfg
        logger.debug(f"Using {config.targets} with {self.defaults} for CC metrics")

        self.harvester = harvesters.CCHarvester(
            config.targets, config=Config(**self.defaults)
        )

    def run(self, module, options):
        """
        Run the operator.

        :param module: The target module path.
        :type  module: ``str``

        :param options: Any runtime options.
        :type  options: ``dict``

        :return: The operator results.
        :rtype: ``dict``
        """
        logger.debug("Running CC harvester")
        results = {}
        for filename, details in dict(self.harvester.results).items():
            results[filename] = {}
            total = 0  # running CC total
            for instance in details:
                if isinstance(instance, Class):
                    i = self._dict_from_class(instance)
                elif isinstance(instance, Function):
                    i = self._dict_from_function(instance)
                else:
                    raise TypeError
                results[filename][i["fullname"]] = i
                del i["fullname"]
                total += i["complexity"]
            results[filename]["complexity"] = total
        return results

    @staticmethod
    def _dict_from_function(l):
        return {
            "name": l.name,
            "is_method": l.is_method,
            "classname": l.classname,
            "closures": l.closures,
            "complexity": l.complexity,
            "fullname": l.fullname,
            "loc": l.endline - l.lineno,
        }

    @staticmethod
    def _dict_from_class(l):
        return {
            "name": l.name,
            "inner_classes": l.inner_classes,
            "real_complexity": l.real_complexity,
            "complexity": l.complexity,
            "fullname": l.fullname,
            "loc": l.endline - l.lineno,
        }
