import 'package:flutter/material.dart';
import '../../models/scenario.dart';
import '../../models/decision.dart';
import '../common/impact_indicator.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class DecisionPanel extends StatefulWidget {
  final Scenario scenario;
  final Function(Decision) onDecisionMade;

  const DecisionPanel({
    Key? key,
    required this.scenario,
    required this.onDecisionMade,
  }) : super(key: key);

  @override
  State<DecisionPanel> createState() => _DecisionPanelState();
}

class _DecisionPanelState extends State<DecisionPanel> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String? selectedApproachId;
  String decisionRationale = '';
  bool showImpacts = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: 2,
      vsync: this,
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Scenario Header
            Row(
              children: [
                Icon(
                  _getScenarioIcon(widget.scenario.category),
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.scenario.title,
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Text(
                        'Difficulty: ${_getDifficultyText(widget.scenario.difficultyLevel)}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                // Time remaining indicator
                if (widget.scenario.timeConstraint != null)
                  _buildTimeIndicator(widget.scenario.timeConstraint!),
              ],
            ),

            const SizedBox(height: 16),

            // Tab Bar for Description/Analysis
            TabBar(
              controller: _tabController,
              tabs: const [
                Tab(text: 'Situation'),
                Tab(text: 'Analysis'),
              ],
            ),

            const SizedBox(height: 16),

            // Tab Content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Situation Tab
                  SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        MarkdownBody(
                          data: widget.scenario.description,
                          styleSheet: MarkdownStyleSheet(
                            p: Theme.of(context).textTheme.bodyLarge,
                          ),
                        ),
                        const SizedBox(height: 16),
                        _buildStakeholderChips(),
                      ],
                    ),
                  ),

                  // Analysis Tab
                  SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Stakeholder Analysis',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 8),
                        _buildStakeholderAnalysis(),
                        const SizedBox(height: 16),
                        Text(
                          'Key Considerations',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 8),
                        _buildKeyConsiderations(),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Decision Options
            Text(
              'Available Approaches',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            _buildApproachOptions(),

            // Rationale Input
            if (selectedApproachId != null) ...[
              const SizedBox(height: 16),
              TextField(
                decoration: const InputDecoration(
                  labelText: 'Decision Rationale',
                  hintText: 'Explain your decision...',
                ),
                maxLines: 2,
                onChanged: (value) => setState(() => decisionRationale = value),
              ),
            ],

            // Submit Button
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: selectedApproachId != null && decisionRationale.isNotEmpty
                    ? _submitDecision
                    : null,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text('Submit Decision'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeIndicator(int timeConstraint) {
    final timeLeft = timeConstraint - widget.scenario.getElapsedTime();
    final progress = timeLeft / timeConstraint;

    return Column(
      children: [
        Text(
          '${timeLeft}m',
          style: TextStyle(
            color: progress < 0.3 ? Colors.red : Colors.grey,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        SizedBox(
          width: 40,
          height: 4,
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(
              progress < 0.3 ? Colors.red : Theme.of(context).primaryColor,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStakeholderChips() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: widget.scenario.stakeholdersAffected.map((stakeholder) {
        return Chip(
          label: Text(stakeholder),
          backgroundColor: Theme.of(context).primaryColorLight,
        );
      }).toList(),
    );
  }

  Widget _buildStakeholderAnalysis() {
    return Column(
      children: widget.scenario.stakeholderAnalysis.entries.map((entry) {
        return ListTile(
          leading: const Icon(Icons.people),
          title: Text(entry.key),
          subtitle: Text(entry.value),
        );
      }).toList(),
    );
  }

  Widget _buildKeyConsiderations() {
    return Column(
      children: widget.scenario.keyConsiderations.map((consideration) {
        return ListTile(
          leading: const Icon(Icons.lightbulb_outline),
          title: Text(consideration),
        );
      }).toList(),
    );
  }

  Widget _buildApproachOptions() {
    return Column(
      children: widget.scenario.possibleApproaches.map((approach) {
        final isSelected = selectedApproachId == approach.id;

        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          elevation: isSelected ? 4 : 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(
              color: isSelected
                  ? Theme.of(context).primaryColor
                  : Colors.transparent,
              width: 2,
            ),
          ),
          child: InkWell(
            onTap: () => setState(() {
              selectedApproachId = approach.id;
              showImpacts = true;
            }),
            borderRadius: BorderRadius.circular(8),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          approach.title,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: isSelected
                                ? Theme.of(context).primaryColor
                                : null,
                          ),
                        ),
                      ),
                      if (isSelected)
                        Icon(
                          Icons.check_circle,
                          color: Theme.of(context).primaryColor,
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(approach.description),
                  if (showImpacts && isSelected) ...[
                    const SizedBox(height: 8),
                    const Divider(),
                    const SizedBox(height: 8),
                    Text(
                      'Potential Impacts',
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: approach.impacts.entries.map((impact) {
                        return ImpactIndicator(
                          label: impact.key,
                          value: impact.value,
                        );
                      }).toList(),
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  void _submitDecision() {
    if (selectedApproachId == null) return;

    final selectedApproach = widget.scenario.possibleApproaches
        .firstWhere((a) => a.id == selectedApproachId);

    final decision = Decision(
      scenarioId: widget.scenario.id,
      approachId: selectedApproachId!,
      rationale: decisionRationale,
      timestamp: DateTime.now(),
    );

    widget.onDecisionMade(decision);
  }

  IconData _getScenarioIcon(String category) {
    switch (category.toLowerCase()) {
      case 'ethics':
        return Icons.balance;
      case 'environment':
        return Icons.eco;
      case 'social':
        return Icons.people;
      case 'governance':
        return Icons.gavel;
      case 'innovation':
        return Icons.lightbulb;
      default:
        return Icons.business;
    }
  }

  String _getDifficultyText(double difficulty) {
    if (difficulty >= 0.8) return 'Hard';
    if (difficulty >= 0.5) return 'Medium';
    return 'Easy';
  }
}