import React, { useState, useEffect } from 'react';
import { Card, Tabs, Typography, Tooltip, Button, Divider, Tag, Space, Progress, List, Row, Col } from 'antd';
import { InfoCircleOutlined, QuestionCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  Node, 
  Edge, 
  NodeTypes, 
  EdgeTypes,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

// Custom node types for agent decision flow
const AgentNode = ({ data }: any) => {
  return (
    <div style={{ 
      padding: '10px', 
      borderRadius: '5px', 
      background: data.isActive ? '#e6f7ff' : '#f0f0f0',
      border: `1px solid ${data.isActive ? '#1890ff' : '#d9d9d9'}`,
      width: 180
    }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 5 }}>
        <div style={{ 
          width: 10, 
          height: 10, 
          borderRadius: '50%', 
          background: data.status === 'completed' ? '#52c41a' : 
                      data.status === 'in_progress' ? '#1890ff' : 
                      data.status === 'error' ? '#f5222d' : '#faad14',
          marginRight: 5 
        }} />
        <Text strong>{data.label}</Text>
      </div>
      <Text type="secondary" style={{ fontSize: 12 }}>{data.description}</Text>
      {data.confidence && (
        <div style={{ marginTop: 5 }}>
          <Text style={{ fontSize: 12 }}>Confidence: </Text>
          <Progress 
            percent={Math.round(data.confidence * 100)} 
            size="small" 
            status={data.confidence > 0.7 ? "success" : data.confidence > 0.4 ? "normal" : "exception"}
            style={{ marginBottom: 0 }}
          />
        </div>
      )}
    </div>
  );
};

const DecisionNode = ({ data }: any) => {
  return (
    <div style={{ 
      padding: '10px', 
      borderRadius: '5px', 
      background: '#fff1b8',
      border: '1px solid #ffd666',
      width: 180
    }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 5 }}>
        <QuestionCircleOutlined style={{ marginRight: 5, color: '#faad14' }} />
        <Text strong>{data.label}</Text>
      </div>
      <Text type="secondary" style={{ fontSize: 12 }}>{data.description}</Text>
      {data.options && (
        <div style={{ marginTop: 5 }}>
          {data.options.map((option: string, index: number) => (
            <Tag 
              key={index} 
              color={data.selectedOption === option ? 'blue' : 'default'}
              style={{ margin: '2px' }}
            >
              {option}
            </Tag>
          ))}
        </div>
      )}
    </div>
  );
};

const DataNode = ({ data }: any) => {
  return (
    <div style={{ 
      padding: '10px', 
      borderRadius: '5px', 
      background: '#f6ffed',
      border: '1px solid #b7eb8f',
      width: 180
    }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 5 }}>
        <InfoCircleOutlined style={{ marginRight: 5, color: '#52c41a' }} />
        <Text strong>{data.label}</Text>
      </div>
      <Text type="secondary" style={{ fontSize: 12 }}>{data.description}</Text>
      {data.source && (
        <div style={{ marginTop: 5 }}>
          <Text type="secondary" style={{ fontSize: 11 }}>Source: {data.source}</Text>
        </div>
      )}
    </div>
  );
};

// Feature importance bar chart component
const FeatureImportanceChart = ({ features }: { features: { name: string; importance: number; direction: 'positive' | 'negative' }[] }) => {
  // Sort features by absolute importance
  const sortedFeatures = [...features].sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance));
  
  return (
    <div>
      {sortedFeatures.map((feature, index) => (
        <div key={index} style={{ marginBottom: 8 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text>{feature.name}</Text>
            <Text strong>{(feature.importance * 100).toFixed(1)}%</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', height: 20 }}>
            {feature.direction === 'negative' && (
              <div 
                style={{ 
                  width: `${Math.abs(feature.importance) * 100}%`, 
                  height: 16, 
                  background: '#ff4d4f',
                  marginRight: 'auto',
                  borderRadius: 2
                }} 
              />
            )}
            <div style={{ width: 2, height: 16, background: '#d9d9d9' }} />
            {feature.direction === 'positive' && (
              <div 
                style={{ 
                  width: `${Math.abs(feature.importance) * 100}%`, 
                  height: 16, 
                  background: '#52c41a',
                  marginLeft: 'auto',
                  borderRadius: 2
                }} 
              />
            )}
          </div>
        </div>
      ))}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <Text type="secondary">Negative Impact</Text>
        <Text type="secondary">Positive Impact</Text>
      </div>
    </div>
  );
};

// Main component for XAI visualizations
const ArcanaVisualizations: React.FC<{
  visualizationType: 'agent_decision' | 'feature_importance' | 'data_lineage';
  data: any;
}> = ({ visualizationType, data }) => {
  // Define node types for ReactFlow
  const nodeTypes: NodeTypes = {
    agentNode: AgentNode,
    decisionNode: DecisionNode,
    dataNode: DataNode,
  };

  // Sample agent decision flow data
  const [agentFlowNodes, setAgentFlowNodes] = useState<Node[]>([
    {
      id: '1',
      type: 'agentNode',
      position: { x: 250, y: 0 },
      data: { 
        label: 'Inventory Analysis', 
        description: 'Analyzing current inventory levels',
        status: 'completed',
        isActive: false,
        confidence: 0.95
      }
    },
    {
      id: '2',
      type: 'dataNode',
      position: { x: 50, y: 100 },
      data: { 
        label: 'Inventory Data', 
        description: 'Current stock levels and trends',
        source: 'ERPNext Inventory Module'
      }
    },
    {
      id: '3',
      type: 'dataNode',
      position: { x: 450, y: 100 },
      data: { 
        label: 'Sales Forecast', 
        description: 'Projected sales for next 30 days',
        source: 'Synapse Forecasting Model'
      }
    },
    {
      id: '4',
      type: 'agentNode',
      position: { x: 250, y: 200 },
      data: { 
        label: 'Reorder Analysis', 
        description: 'Determining optimal reorder quantities',
        status: 'completed',
        isActive: true,
        confidence: 0.87
      }
    },
    {
      id: '5',
      type: 'decisionNode',
      position: { x: 250, y: 300 },
      data: { 
        label: 'Reorder Decision', 
        description: 'Should we reorder this product?',
        options: ['Yes', 'No', 'Defer'],
        selectedOption: 'Yes'
      }
    },
    {
      id: '6',
      type: 'agentNode',
      position: { x: 250, y: 400 },
      data: { 
        label: 'PO Creation', 
        description: 'Creating purchase order',
        status: 'in_progress',
        isActive: false,
        confidence: 0.92
      }
    }
  ]);

  // Sample agent decision flow edges
  const [agentFlowEdges, setAgentFlowEdges] = useState<Edge[]>([
    {
      id: 'e1-2',
      source: '1',
      target: '2',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },
    {
      id: 'e1-3',
      source: '1',
      target: '3',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },
    {
      id: 'e2-4',
      source: '2',
      target: '4',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },
    {
      id: 'e3-4',
      source: '3',
      target: '4',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },
    {
      id: 'e4-5',
      source: '4',
      target: '5',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },
    {
      id: 'e5-6',
      source: '5',
      target: '6',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    }
  ]);

  // Sample feature importance data
  const [featureImportanceData, setFeatureImportanceData] = useState([
    { name: 'Current Stock Level', importance: -0.35, direction: 'negative' as const },
    { name: 'Historical Sales Velocity', importance: 0.25, direction: 'positive' as const },
    { name: 'Supplier Lead Time', importance: -0.18, direction: 'negative' as const },
    { name: 'Seasonal Demand Factor', importance: 0.12, direction: 'positive' as const },
    { name: 'Price Elasticity', importance: 0.08, direction: 'positive' as const },
    { name: 'Carrying Cost', importance: -0.05, direction: 'negative' as const },
  ]);

  // Sample data lineage information
  const [dataLineageInfo, setDataLineageInfo] = useState([
    {
      id: '1',
      name: 'Inventory Records',
      type: 'Primary Data',
      source: 'ERPNext Inventory Module',
      lastUpdated: '2023-07-15 14:32:00',
      fields: ['SKU', 'Quantity', 'Location', 'Cost'],
      confidence: 0.99
    },
    {
      id: '2',
      name: 'Sales History',
      type: 'Primary Data',
      source: 'ERPNext Sales Module',
      lastUpdated: '2023-07-15 18:45:00',
      fields: ['SKU', 'Quantity', 'Date', 'Customer'],
      confidence: 0.99
    },
    {
      id: '3',
      name: 'Sales Forecast',
      type: 'Derived Data',
      source: 'Synapse Forecasting Model',
      lastUpdated: '2023-07-15 19:00:00',
      fields: ['SKU', 'Predicted Quantity', 'Confidence Interval'],
      confidence: 0.87,
      derivedFrom: ['Sales History', 'Seasonal Factors']
    },
    {
      id: '4',
      name: 'Reorder Recommendation',
      type: 'Agent Output',
      source: 'Inventory Management Agent',
      lastUpdated: '2023-07-15 19:15:00',
      fields: ['SKU', 'Reorder Quantity', 'Urgency'],
      confidence: 0.92,
      derivedFrom: ['Inventory Records', 'Sales Forecast', 'Supplier Data']
    }
  ]);

  // Render different visualization types
  const renderVisualization = () => {
    switch (visualizationType) {
      case 'agent_decision':
        return (
          <div style={{ height: 500 }}>
            <ReactFlow
              nodes={agentFlowNodes}
              edges={agentFlowEdges}
              nodeTypes={nodeTypes}
              fitView
            >
              <Controls />
              <MiniMap />
              <Background />
            </ReactFlow>
          </div>
        );
      
      case 'feature_importance':
        return (
          <div>
            <Title level={4}>Factors Influencing Reorder Decision</Title>
            <Paragraph>
              The following factors influenced the agent's decision to recommend reordering SKU-1234.
              Factors with positive impact support reordering, while negative factors oppose it.
            </Paragraph>
            <FeatureImportanceChart features={featureImportanceData} />
            <Divider />
            <Row gutter={16}>
              <Col span={12}>
                <Card title="Decision Summary" size="small">
                  <Paragraph>
                    <Text strong>Decision: </Text>
                    <Tag color="green">Reorder Recommended</Tag>
                  </Paragraph>
                  <Paragraph>
                    <Text strong>Confidence: </Text>
                    <Progress percent={87} size="small" />
                  </Paragraph>
                  <Paragraph>
                    <Text strong>Recommended Quantity: </Text>
                    250 units
                  </Paragraph>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Alternative Scenarios" size="small">
                  <List
                    size="small"
                    dataSource={[
                      { scenario: 'If sales velocity increases by 10%', outcome: 'Reorder 300 units' },
                      { scenario: 'If supplier lead time decreases by 5 days', outcome: 'Reorder 200 units' },
                      { scenario: 'If current stock increases by 100 units', outcome: 'Defer reorder by 2 weeks' }
                    ]}
                    renderItem={item => (
                      <List.Item>
                        <Text strong>{item.scenario}: </Text>
                        <Text>{item.outcome}</Text>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
            </Row>
          </div>
        );
      
      case 'data_lineage':
        return (
          <div>
            <Title level={4}>Data Provenance</Title>
            <Paragraph>
              This visualization shows the origin and flow of data used in making the reorder recommendation.
            </Paragraph>
            <List
              itemLayout="vertical"
              dataSource={dataLineageInfo}
              renderItem={item => (
                <List.Item>
                  <Card 
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>{item.name}</span>
                        <Tag color={
                          item.type === 'Primary Data' ? 'green' : 
                          item.type === 'Derived Data' ? 'blue' : 'purple'
                        }>
                          {item.type}
                        </Tag>
                      </div>
                    }
                    size="small"
                  >
                    <Paragraph>
                      <Text strong>Source: </Text>
                      {item.source}
                    </Paragraph>
                    <Paragraph>
                      <Text strong>Last Updated: </Text>
                      {item.lastUpdated}
                    </Paragraph>
                    <Paragraph>
                      <Text strong>Fields Used: </Text>
                      {item.fields.map((field, index) => (
                        <Tag key={index}>{field}</Tag>
                      ))}
                    </Paragraph>
                    {item.derivedFrom && (
                      <Paragraph>
                        <Text strong>Derived From: </Text>
                        {item.derivedFrom.map((source, index) => (
                          <Tag key={index} color="blue">{source}</Tag>
                        ))}
                      </Paragraph>
                    )}
                    <Paragraph>
                      <Text strong>Confidence: </Text>
                      <Progress percent={Math.round(item.confidence * 100)} size="small" />
                    </Paragraph>
                  </Card>
                </List.Item>
              )}
            />
          </div>
        );
      
      default:
        return <div>Please select a visualization type</div>;
    }
  };

  return (
    <Card title="Arcana XAI Visualization" className="arcana-visualization">
      <Tabs defaultActiveKey="1">
        <TabPane tab="Agent Decision Flow" key="1">
          {renderVisualization()}
        </TabPane>
        <TabPane tab="Feature Importance" key="2">
          <FeatureImportanceChart features={featureImportanceData} />
        </TabPane>
        <TabPane tab="Data Lineage" key="3">
          <div style={{ height: 500 }}>
            {/* Data lineage visualization would go here */}
            <Title level={4}>Data Provenance</Title>
            <Paragraph>
              This visualization shows the origin and flow of data used in making the reorder recommendation.
            </Paragraph>
            <List
              itemLayout="vertical"
              dataSource={dataLineageInfo.slice(0, 2)}
              renderItem={item => (
                <List.Item>
                  <Card 
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>{item.name}</span>
                        <Tag color={
                          item.type === 'Primary Data' ? 'green' : 
                          item.type === 'Derived Data' ? 'blue' : 'purple'
                        }>
                          {item.type}
                        </Tag>
                      </div>
                    }
                    size="small"
                  >
                    <Paragraph>
                      <Text strong>Source: </Text>
                      {item.source}
                    </Paragraph>
                    <Paragraph>
                      <Text strong>Last Updated: </Text>
                      {item.lastUpdated}
                    </Paragraph>
                  </Card>
                </List.Item>
              )}
            />
          </div>
        </TabPane>
      </Tabs>
    </Card>
  );
};

export default ArcanaVisualizations;