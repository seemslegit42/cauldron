import React, { useState } from 'react';
import { Typography, Card, Input, List, Tag, Space, Avatar, Button, Divider } from 'antd';
import { SearchOutlined, FileTextOutlined, UserOutlined, BookOutlined, PlusOutlined, SafetyOutlined, ToolOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { Search } = Input;

const Knowledge: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Mock knowledge data
  const knowledgeItems = [
    { 
      id: 1, 
      title: 'Introduction to Cauldron™ sEOS', 
      type: 'document', 
      tags: ['overview', 'getting-started'], 
      author: 'System Admin',
      updated: '2 days ago',
      excerpt: 'This document provides an overview of the Cauldron™ Sentient Enterprise Operating System...'
    },
    { 
      id: 2, 
      title: 'Configuring Synapse™ for Predictive Analytics', 
      type: 'guide', 
      tags: ['synapse', 'analytics', 'configuration'], 
      author: 'Data Science Team',
      updated: '1 week ago',
      excerpt: 'Learn how to configure the Synapse™ module to generate predictive analytics and forecasts...'
    },
    { 
      id: 3, 
      title: 'Security Best Practices for Aegis Protocol™', 
      type: 'policy', 
      tags: ['security', 'compliance', 'best-practices'], 
      author: 'Security Officer',
      updated: '3 weeks ago',
      excerpt: 'This policy document outlines the security best practices when working with Aegis Protocol™...'
    },
    { 
      id: 4, 
      title: 'Troubleshooting Common ERPNext Issues', 
      type: 'troubleshooting', 
      tags: ['operations', 'erpnext', 'troubleshooting'], 
      author: 'Support Team',
      updated: '1 month ago',
      excerpt: 'A guide to resolving common issues encountered in the Operations Core module based on ERPNext...'
    },
  ];

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    // In a real implementation, this would trigger a search against the Lore™ module
  };

  const getIconForType = (type: string) => {
    switch (type) {
      case 'document':
        return <FileTextOutlined />;
      case 'guide':
        return <BookOutlined />;
      case 'policy':
        return <SafetyOutlined />;
      case 'troubleshooting':
        return <ToolOutlined />;
      default:
        return <FileTextOutlined />;
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={2}>Lore™ Knowledge</Title>
          <Paragraph>Access and manage your organization's collective intelligence.</Paragraph>
        </div>
        <Button type="primary" icon={<PlusOutlined />}>
          New Document
        </Button>
      </div>
      
      <Card style={{ marginBottom: 16 }}>
        <Search
          placeholder="Ask a question or search for knowledge..."
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          onSearch={handleSearch}
        />
      </Card>
      
      <Card title="Knowledge Repository">
        <List
          itemLayout="vertical"
          size="large"
          dataSource={knowledgeItems}
          renderItem={item => (
            <List.Item
              key={item.id}
              actions={[
                <Space>
                  <UserOutlined />
                  <Text>{item.author}</Text>
                </Space>,
                <Text type="secondary">Updated {item.updated}</Text>
              ]}
              extra={
                <Space>
                  {item.tags.map(tag => (
                    <Tag key={tag} color="blue">{tag}</Tag>
                  ))}
                </Space>
              }
            >
              <List.Item.Meta
                avatar={<Avatar icon={getIconForType(item.type)} />}
                title={<a href="#">{item.title}</a>}
                description={<Tag color="purple">{item.type.toUpperCase()}</Tag>}
              />
              {item.excerpt}
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Knowledge;