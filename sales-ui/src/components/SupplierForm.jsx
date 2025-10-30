import React, { useState } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, IdcardOutlined } from '@ant-design/icons';
import ApiService from '../api/ApiService';

const SupplierForm = ({ visible, onCancel, onFinish, supplier }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const isEditing = !!supplier;

  const onOk = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();

      if (isEditing) {
        await ApiService.updateSupplier(supplier.id, values);
        message.success('Fornecedor atualizado com sucesso!');
      } else {
        await ApiService.createSupplier(values);
        message.success('Fornecedor criado com sucesso!');
      }
      onFinish();
    } catch (error) {
      message.error('Ocorreu um erro ao guardar o fornecedor.');
      console.error('Validation Failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={isEditing ? 'Editar Fornecedor' : 'Criar Novo Fornecedor'}
      visible={visible}
      onCancel={onCancel}
      destroyOnClose
      footer={[
        <Button key="back" onClick={onCancel}>
          Cancelar
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={onOk}>
          Guardar
        </Button>,
      ]}
    >
      <Form form={form} layout="vertical" initialValues={supplier || {}}>
        <Form.Item name="name" label="Nome do Fornecedor" rules={[{ required: true, message: 'O nome é obrigatório' }]}>
          <Input prefix={<IdcardOutlined />} placeholder="Nome da Empresa" />
        </Form.Item>
        <Form.Item name="contact_person" label="Pessoa de Contacto">
          <Input prefix={<UserOutlined />} placeholder="João da Silva" />
        </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ type: 'email', message: 'Insira um email válido' }]}>
          <Input prefix={<MailOutlined />} placeholder="contacto@empresa.com" />
        </Form.Item>
        <Form.Item name="phone_number" label="Telefone">
          <Input prefix={<PhoneOutlined />} placeholder="(XX) XXXXX-XXXX" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default SupplierForm;